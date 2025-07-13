import json
import logging
from typing import List, Dict, Optional
from RAG.openrouter_client import openrouter_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReviewRefiner:
    def __init__(self, max_iterations: int = 2, min_relevant_reviews: int = 3):
        self.max_iterations = max_iterations
        self.min_relevant_reviews = min_relevant_reviews
        
    def is_review_relevant(self, review: str, place_name: str, place_type: str = "place") -> bool:
        """
        Use LLM to determine if a review is relevant to the specific place.
        """
        prompt = f"""
        You are a review relevance checker. Determine if this review is relevant to the specific place.
        
        Place: {place_name}
        Place Type: {place_type}
        Review: {review}
        
        Consider:
        1. Does the review mention the specific place name or location?
        2. Does it describe experiences at this place?
        3. Is it about the same type of establishment (restaurant, bar, park, etc.)?
        4. Does it contain useful information about the place?
        
        Respond with ONLY "YES" or "NO".
        """
        
        try:
            response = openrouter_client.generate_content(prompt)
            result = response.strip().upper()
            logger.debug(f"LLM response for review relevance: {result}")
            return result == "YES"
        except Exception as e:
            logger.error(f"Error checking review relevance: {e}")
            # Fallback: if we can't determine, assume it's relevant
            return True
    
    def _build_batch_prompt(self, reviews: List[str], place_name: str, place_type: str = "place") -> str:
        """
        Build a batch prompt for multiple reviews.
        """
        numbered_reviews = []
        for i, review in enumerate(reviews, 1):
            numbered_reviews.append(f"{i}. {review}")
        
        reviews_text = "\n".join(numbered_reviews)
        
        prompt = f"""
        You are a review relevance checker. Determine if each review is relevant to the specific place.
        
        Place: {place_name}
        Place Type: {place_type}
        
        Reviews:
        {reviews_text}
        
        Consider for each review:
        1. Does the review mention the specific place name or location?
        2. Does it describe experiences at this place?
        3. Is it about the same type of establishment (restaurant, bar, park, etc.)?
        4. Does it contain useful information about the place?
        
        Respond with ONLY "YES" or "NO" for each review, one per line, in the same order as the reviews.
        Example:
        YES
        NO
        YES
        """
        
        return prompt
    
    def filter_relevant_reviews_batched(self, reviews: List[str], place_name: str, place_type: str = "place") -> List[str]:
        """
        Filter reviews in batches to reduce LLM calls.
        """
        if not reviews:
            return []
        
        relevant_reviews = []
        batch_size = 15
        
        # Process reviews in batches
        for i in range(0, len(reviews), batch_size):
            batch = reviews[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} with {len(batch)} reviews")
            
            try:
                # Build batch prompt
                prompt = self._build_batch_prompt(batch, place_name, place_type)
                
                # Get LLM response
                response = openrouter_client.generate_content(prompt)
                result = response.strip()
                
                logger.debug(f"LLM batch response: {result}")
                
                # Parse line-by-line responses
                lines = result.split('\n')
                relevant_indices = []
                
                for j, line in enumerate(lines):
                    line = line.strip().upper()
                    if line == "YES":
                        relevant_indices.append(j)
                
                # Add relevant reviews from this batch
                for idx in relevant_indices:
                    if idx < len(batch):
                        relevant_reviews.append(batch[idx])
                
                logger.info(f"Batch {i//batch_size + 1}: {len(relevant_indices)} relevant out of {len(batch)}")
                
            except Exception as e:
                logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                # Conservative fallback: assume all reviews in batch are relevant
                logger.warning(f"Fallback: assuming all {len(batch)} reviews in batch are relevant")
                relevant_reviews.extend(batch)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_relevant = []
        for review in relevant_reviews:
            if review not in seen:
                seen.add(review)
                unique_relevant.append(review)
        
        logger.info(f"Filtered {len(unique_relevant)} relevant reviews out of {len(reviews)} total reviews")
        return unique_relevant
    
    def filter_relevant_reviews(self, reviews: List[str], place_name: str, place_type: str = "place") -> List[str]:
        """
        Filter reviews to only include those relevant to the specific place.
        """
        relevant_reviews = []
        
        for review in reviews:
            if self.is_review_relevant(review, place_name, place_type):
                relevant_reviews.append(review)
                
        logger.info(f"Filtered {len(relevant_reviews)} relevant reviews out of {len(reviews)} total reviews")
        return relevant_reviews
    
    def refine_reviews_with_llm(self, 
                               initial_reviews: List[str], 
                               place_name: str, 
                               place_type: str = "place",
                               fetch_more_reviews_func=None,
                               **fetch_kwargs) -> List[str]:
        """
        Main function to refine reviews using LLM filtering with iterative deepening.
        
        Args:
            initial_reviews: Initial list of reviews to filter
            place_name: Name of the place to check relevance against
            place_type: Type of place (restaurant, bar, park, etc.)
            fetch_more_reviews_func: Function to call to get more reviews if needed
            **fetch_kwargs: Additional arguments to pass to fetch function
        """
        current_reviews = initial_reviews.copy()
        relevant_reviews = []
        iteration = 0
        
        logger.info(f"Starting review refinement for {place_name}. Initial reviews: {len(current_reviews)}")
        
        while iteration < self.max_iterations:
            logger.info(f"Iteration {iteration + 1}/{self.max_iterations}")
            
            # Filter current reviews for relevance using batched processing
            iteration_relevant = self.filter_relevant_reviews_batched(current_reviews, place_name, place_type)
            relevant_reviews.extend(iteration_relevant)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_relevant = []
            for review in relevant_reviews:
                if review not in seen:
                    seen.add(review)
                    unique_relevant.append(review)
            relevant_reviews = unique_relevant
            
            logger.info(f"Total relevant reviews so far: {len(relevant_reviews)}")
            
            # Check if we have enough relevant reviews
            if len(relevant_reviews) >= self.min_relevant_reviews:
                logger.info(f"Found sufficient relevant reviews ({len(relevant_reviews)})")
                return relevant_reviews[:self.min_relevant_reviews]  # Return only the minimum needed
            
            # If we don't have enough and we can fetch more
            if fetch_more_reviews_func and iteration < self.max_iterations - 1:
                logger.info(f"Need more reviews. Fetching additional reviews...")
                try:
                    # Extract review content from the fetched reviews
                    new_reviews = fetch_more_reviews_func(**fetch_kwargs)
                    if new_reviews:
                        # Convert review dictionaries to content strings
                        new_review_contents = [review.get('content', '') for review in new_reviews]
                        current_reviews = new_review_contents
                        logger.info(f"Fetched {len(new_reviews)} additional reviews")
                    else:
                        logger.warning("No more reviews available to fetch")
                        break
                except Exception as e:
                    logger.error(f"Error fetching more reviews: {e}")
                    break
            else:
                logger.info("No more iterations or fetch function available")
                break
            
            iteration += 1
        
        logger.info(f"Review refinement completed. Final relevant reviews: {len(relevant_reviews)}")
        return relevant_reviews

def create_review_refiner(max_iterations: int = 2, min_relevant_reviews: int = 3) -> ReviewRefiner:
    """
    Factory function to create a ReviewRefiner instance.
    """
    return ReviewRefiner(max_iterations=max_iterations, min_relevant_reviews=min_relevant_reviews) 