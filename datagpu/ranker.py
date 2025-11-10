"""Dataset ranking and quality scoring module."""

from typing import Tuple, Dict, Optional
import polars as pl
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from datagpu.types import RankMethod


class DataRanker:
    """Handles dataset ranking by quality/relevance."""
    
    def __init__(self, method: RankMethod = RankMethod.RELEVANCE, verbose: bool = True):
        self.method = method
        self.verbose = verbose
        self.vectorizer = None
    
    def _get_text_columns(self, df: pl.DataFrame) -> list:
        """Identify text columns in dataframe."""
        text_cols = []
        for col in df.columns:
            if df[col].dtype in [pl.Utf8, pl.Categorical]:
                text_cols.append(col)
        return text_cols
    
    def _combine_text_columns(self, df: pl.DataFrame, text_cols: list) -> list:
        """Combine multiple text columns into single strings."""
        if not text_cols:
            return [""] * len(df)
        
        combined = df.select([
            pl.concat_str([pl.col(c).cast(pl.Utf8) for c in text_cols], separator=" ")
        ]).to_series().to_list()
        
        return combined
    
    def rank_tfidf(self, df: pl.DataFrame, target_query: Optional[str] = None) -> Tuple[pl.DataFrame, Dict[str, int]]:
        """
        Rank rows using TF-IDF scoring.
        
        Args:
            df: Input dataframe
            target_query: Optional target query for relevance ranking
        
        Returns:
            Tuple of (ranked dataframe with quality_score column, stats dict)
        """
        text_cols = self._get_text_columns(df)
        
        if not text_cols:
            # No text columns, assign uniform scores
            df = df.with_columns(pl.lit(1.0).alias("quality_score"))
            return df, {"ranked_samples": len(df), "method": "uniform"}
        
        # Combine text columns
        texts = self._combine_text_columns(df, text_cols)
        
        # Compute TF-IDF
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=2
        )
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
        except ValueError:
            # Not enough documents or features
            df = df.with_columns(pl.lit(1.0).alias("quality_score"))
            return df, {"ranked_samples": len(df), "method": "uniform"}
        
        if target_query:
            # Rank by similarity to target query
            query_vec = self.vectorizer.transform([target_query])
            scores = cosine_similarity(tfidf_matrix, query_vec).flatten()
        else:
            # Rank by document importance (sum of TF-IDF scores)
            scores = np.asarray(tfidf_matrix.sum(axis=1)).flatten()
            # Normalize to [0, 1]
            if scores.max() > 0:
                scores = scores / scores.max()
        
        # Add quality scores to dataframe
        df = df.with_columns(pl.Series("quality_score", scores))
        
        # Sort by quality score descending
        df = df.sort("quality_score", descending=True)
        
        stats = {
            "ranked_samples": len(df),
            "method": "tfidf",
            "avg_score": float(scores.mean()),
            "max_score": float(scores.max()),
            "min_score": float(scores.min())
        }
        
        return df, stats
    
    def rank_cosine(self, df: pl.DataFrame, target_query: Optional[str] = None) -> Tuple[pl.DataFrame, Dict[str, int]]:
        """
        Rank rows using cosine similarity.
        
        This is similar to TF-IDF but focuses on similarity to a target.
        """
        return self.rank_tfidf(df, target_query)
    
    def rank(self, df: pl.DataFrame, target_query: Optional[str] = None) -> Tuple[pl.DataFrame, Dict[str, int]]:
        """
        Rank dataset based on configured method.
        
        Args:
            df: Input dataframe
            target_query: Optional target query for relevance ranking
        
        Returns:
            Tuple of (ranked dataframe, stats dict)
        """
        if self.method == RankMethod.NONE:
            df = df.with_columns(pl.lit(1.0).alias("quality_score"))
            return df, {"ranked_samples": len(df), "method": "none"}
        
        elif self.method in [RankMethod.TFIDF, RankMethod.RELEVANCE]:
            return self.rank_tfidf(df, target_query)
        
        elif self.method == RankMethod.COSINE:
            return self.rank_cosine(df, target_query)
        
        else:
            raise ValueError(f"Unknown ranking method: {self.method}")
