from typing import List

class TextChunker:
    WORDS_PER_CHUNK = 350
    MAX_CHARS_PER_CHUNK = 1500

    def chunk(self, text: str, max_chunks=10) -> List[str]:
        """
        Splits text into ~350-word chunks.
        Each chunk is then truncated to 1500 characters to stay within BERT bounds.
        """
        if not text:
            return []
            
        words = text.split()
        chunks = []
        
        # Slice words into chunks of 350
        for i in range(0, len(words), self.WORDS_PER_CHUNK):
            if len(chunks) >= max_chunks:
                break
            
            chunk_words = words[i:i + self.WORDS_PER_CHUNK]
            chunk_text = " ".join(chunk_words)
            
            # Truncate to 1500 chars 
            if len(chunk_text) > self.MAX_CHARS_PER_CHUNK:
                chunk_text = chunk_text[:self.MAX_CHARS_PER_CHUNK]
            
            chunks.append(chunk_text)
            
        return chunks

    def get_chunk_weights(self, chunks: List[str]) -> List[float]:
        """
        Calculates weights for normalized aggregation.
        First chunk gets 2.0 weight (lede/headline importance).
        All subsequent chunks get 1.0.
        """
        n = len(chunks)
        if n == 0:
            return []
        if n == 1:
            return [1.0]
            
        weights = [2.0] + [1.0] * (n - 1)
        total = sum(weights)
        return [w / total for w in weights]
