#!/usr/bin/env python3
"""
Step 3: Generation Component
Uses GPT-4 to generate answers based on augmented context
"""

import logging
import time
from typing import Dict, Any, Optional
from openai import AzureOpenAI
from config import config
from config.hyperparameters import RAGHyperparameters
from config.prompts import RAGPrompts

logger = logging.getLogger(__name__)

class GenerationComponent:
    """Step 3: Generates answers using GPT-4 with augmented context"""
    
    def __init__(self):
        """Initialize the generation component"""
        # Initialize OpenAI client
        self.openai_client = AzureOpenAI(
            api_key=config.Config.AZURE_OPENAI_API_KEY,
            api_version=config.Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=config.Config.AZURE_OPENAI_ENDPOINT
        )
        
        logger.info("Generation component initialized")
    
    def generate(self, question: str, context: str, temperature: float = None, 
                max_tokens: int = None) -> Dict[str, Any]:
        """
        Generate answer using GPT-4 with context
        
        Args:
            question: The user's question
            context: Augmented context from retrieval
            temperature: Response creativity (0.0-1.0)
            max_tokens: Maximum response length
            
        Returns:
            Dictionary with generated answer and metadata
        """
        try:
            # Use hyperparameters for defaults
            temperature = temperature or RAGHyperparameters.DEFAULT_TEMPERATURE
            max_tokens = max_tokens or RAGHyperparameters.DEFAULT_MAX_TOKENS
            
            # Validate parameters
            max_tokens = min(max_tokens, RAGHyperparameters.MAX_MAX_TOKENS)
            max_tokens = max(max_tokens, RAGHyperparameters.MIN_MAX_TOKENS)
            
            start_time = time.time()
            logger.info(f"Generating answer for question: '{question[:50]}...'")
            
            if not context.strip():
                logger.warning("No context provided for generation")
                return {
                    'answer': "I don't have enough information to answer your question. Please try rephrasing or ask about a different topic.",
                    'confidence': 0.0,
                    'tokens_used': 0,
                    'generation_time': 0.0,
                    'error': 'No context available'
                }
            
            # Generate answer using GPT-4
            result = self._generate_with_gpt4(question, context, temperature, max_tokens)
            
            generation_time = time.time() - start_time
            result['generation_time'] = generation_time
            
            logger.info(f"Generated answer in {generation_time:.3f}s, tokens: {result.get('tokens_used', 0)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in generation: {e}")
            return {
                'answer': f"Sorry, I encountered an error while generating an answer: {str(e)}",
                'confidence': 0.0,
                'tokens_used': 0,
                'generation_time': time.time() - start_time,
                'error': str(e)
            }
    
    def _generate_with_gpt4(self, question: str, context: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        """
        Generate answer using GPT-4
        
        Args:
            question: The user's question
            context: Augmented context
            temperature: Response creativity
            max_tokens: Maximum response length
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Prepare the prompt using centralized prompts
            system_prompt = RAGPrompts.RAG_SYSTEM_PROMPT
            user_prompt = RAGPrompts.RAG_USER_PROMPT_TEMPLATE.format(
                context=context,
                question=question
            )
            
            # Generate response
            response = self.openai_client.chat.completions.create(
                model=config.Config.GPT4_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=RAGHyperparameters.TOP_P,
                frequency_penalty=RAGHyperparameters.FREQUENCY_PENALTY,
                presence_penalty=RAGHyperparameters.PRESENCE_PENALTY
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Calculate confidence based on response quality
            confidence = self._calculate_confidence(answer, context, question)
            
            return {
                'answer': answer,
                'confidence': confidence,
                'model': config.Config.GPT4_MODEL,
                'tokens_used': response.usage.total_tokens,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }
            
        except Exception as e:
            logger.error(f"Error generating with GPT-4: {e}")
            return {
                'answer': f"Sorry, I couldn't generate an answer due to an error: {str(e)}",
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _calculate_confidence(self, answer: str, context: str, question: str) -> float:
        """
        Calculate confidence score for the generated answer
        
        Args:
            answer: Generated answer
            context: Used context
            question: Original question
            
        Returns:
            Confidence score (0.0-1.0)
        """
        try:
            confidence = RAGHyperparameters.BASE_CONFIDENCE
            
            # Check if answer is not empty
            if not answer.strip():
                return 0.0
            
            # Check if answer is too short
            if len(answer) < RAGHyperparameters.MIN_ANSWER_LENGTH:
                confidence -= RAGHyperparameters.SHORT_ANSWER_PENALTY
            
            # Check if answer is too long (might be rambling)
            if len(answer) > RAGHyperparameters.MAX_ANSWER_LENGTH:
                confidence -= RAGHyperparameters.LONG_ANSWER_PENALTY
            
            # Check if answer contains uncertainty indicators
            uncertainty_words = ['i don\'t know', 'not sure', 'unclear', 'no information', 'cannot answer']
            if any(word in answer.lower() for word in uncertainty_words):
                confidence -= RAGHyperparameters.UNCERTAINTY_PENALTY
            
            # Check if answer references the context
            if 'based on' in answer.lower() or 'according to' in answer.lower():
                confidence += RAGHyperparameters.CONTEXT_REFERENCE_BONUS
            
            # Ensure confidence is within bounds
            confidence = max(0.0, min(1.0, confidence))
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5  # Default confidence
    
    def validate_answer(self, answer: str, question: str) -> Dict[str, Any]:
        """
        Validate the generated answer
        
        Args:
            answer: Generated answer
            question: Original question
            
        Returns:
            Validation results
        """
        try:
            validation = {
                'is_valid': True,
                'length': len(answer),
                'has_content': bool(answer.strip()),
                'issues': []
            }
            
            # Check if answer is empty
            if not answer.strip():
                validation['is_valid'] = False
                validation['issues'].append("Answer is empty")
            
            # Check if answer is too short
            if len(answer) < 10:
                validation['issues'].append("Answer is very short")
            
            # Check if answer is too long
            if len(answer) > 2000:
                validation['issues'].append("Answer is very long")
            
            # Check for common error patterns
            error_patterns = [
                "i don't have enough information",
                "i cannot answer",
                "i don't know",
                "no information available"
            ]
            
            for pattern in error_patterns:
                if pattern in answer.lower():
                    validation['issues'].append(f"Contains error pattern: '{pattern}'")
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating answer: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'issues': ['Validation error occurred']
            }
    
    def get_generation_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get summary of generation process
        
        Args:
            result: Generation result dictionary
            
        Returns:
            Summary dictionary
        """
        try:
            return {
                'model_used': result.get('model', 'unknown'),
                'tokens_used': result.get('tokens_used', 0),
                'prompt_tokens': result.get('prompt_tokens', 0),
                'completion_tokens': result.get('completion_tokens', 0),
                'generation_time': result.get('generation_time', 0.0),
                'confidence': result.get('confidence', 0.0),
                'answer_length': len(result.get('answer', ''))
            }
            
        except Exception as e:
            logger.error(f"Error getting generation summary: {e}")
            return {'error': str(e)} 