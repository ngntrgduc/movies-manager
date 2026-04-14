import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from utils.constants import UNWATCHED_STATUS

def build_item_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Build a numeric feature matrix for item-based recommendation."""

    df_features = df.copy()
    df_features = df_features.drop(columns=['rating', 'watched_date'])

    # Min-max scaling year column
    min_year, max_year =  df['year'].min(), df['year'].max()
    df_features['year'] = (df['year'] - min_year) / (max_year - min_year)
    df_features['year'] *= 0.2  # Downweight because same year doesn't mean high similarity

    country_features = df['country'].str.get_dummies()
    country_features *= 0.4
    
    type_features = df['type'].str.get_dummies()
    type_features *= 0.5
    
    genres_features = df['genres'].str.get_dummies(',')

    return pd.concat(
        [
            df_features.drop(columns=['id', 'name', 'status', 'type', 'country', 'genres']), 
            type_features, country_features, genres_features
        ], axis=1
    )


def build_item_similarity_matrix(feature_matrix: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """Compute cosine similarity between all items."""

    similarity_matrix = cosine_similarity(feature_matrix)
    return pd.DataFrame(
        similarity_matrix, 
        index=df['id'], 
        columns=df['id']
    )

def recommend(movie_id: int, df: pd.DataFrame, top_k: int = 5) -> pd.DataFrame:
    """Recommend similar unwatched movies based on cosine similarity."""

    feature_matrix = build_item_feature_matrix(df) 
    similarity_df = build_item_similarity_matrix(feature_matrix, df)

    if movie_id not in similarity_df.index:
        return f'Movie ID {movie_id} not found.'

    sim_scores = similarity_df.loc[movie_id].drop(movie_id)  # remove itself

    # Keep unwatched movies
    unwatched_ids = df[df['status'] == UNWATCHED_STATUS]['id']
    sim_scores = sim_scores[sim_scores.index.isin(unwatched_ids)]
    
    top_ids = sim_scores.sort_values(ascending=False).head(top_k).index
    return df.set_index('id').loc[top_ids].reset_index()

def recommend_from_user_profile(
    user_profile,
    df: pd.DataFrame,
    feature_matrix: pd.DataFrame,
    top_k: int = 5
) -> pd.DataFrame:
    """Rank movies based on similarity to a user profile."""

    similarity_scores = cosine_similarity([user_profile], feature_matrix).flatten()
    sim_series = pd.Series(similarity_scores, index=df['id'])

    unwatched_ids = df[df['status'] == UNWATCHED_STATUS]['id']
    sim_series = sim_series.loc[unwatched_ids]
    top_ids = sim_series.sort_values(ascending=False).head(top_k).index

    return df.set_index('id').loc[top_ids].reset_index()  # preserve ranking orders

def recommend_recent_profile(
    df: pd.DataFrame, 
    feature_matrix: pd.DataFrame, 
    profile_size: int = 5, 
    top_k: int = 5
) -> pd.DataFrame:
    """Recommend movies using a user profile built from recently watched movies."""

    watched_df = df[df['status'] == 'completed']
    recent = watched_df.sort_values('watched_date', ascending=False).head(profile_size)
    
    user_profile = feature_matrix.loc[recent.index].mean(axis=0)

    return recommend_from_user_profile(user_profile, df, feature_matrix, top_k)

def recommend_all_profile(
    df: pd.DataFrame, 
    feature_matrix: pd.DataFrame, 
    top_k: int = 5,
    half_life_days: int = 180,
) -> pd.DataFrame:
    """
    Recommend movies using a user profile built from all completed movies.

    The user profile is a weighted average of movie feature vectors where
    weights combine rating weighting x exponential time decay based on watch date

    More recent and higher-rated movies influence the profile more strongly.
    """

    import numpy as np

    def half_life(days) -> float:
        """Convert a half-life value (in days) to the exponential decay rate."""
        return np.log(2) / days

    def exponential_decay(t, decay_rate: float = 0.01) -> np.ndarray:
        """Compute exponential decay weights."""
        return np.exp(-decay_rate*t)

    def normalize_watched_date(date_str):
        """Normalize watched_date values into pandas Timestamp."""
        if pd.isna(date_str):
            return None
        
        date_str = str(date_str)

        # convert to mid-year for year-only and year with month data, mid-year is 1 July
        if len(date_str) == 4:  # YYYY
            return pd.Timestamp(f'{date_str}-07-01')

        if len(date_str) == 7:  # YYYY-MM
            return pd.Timestamp(f'{date_str}-15')

        return pd.Timestamp(date_str)

    watched_df = df[df['status'] == 'completed']
    
    watched_features = feature_matrix.loc[watched_df.index]
    
    rating_weights = (watched_df['rating'] / 10) ** 2  # see notebooks/rating_weight.ipynb
    
    watched_date = watched_df['watched_date'].apply(normalize_watched_date)
    today = pd.Timestamp.today().normalize()  # .normalize() removes the time portion
    days_since_watch = (today - watched_date).dt.days

    decay_rate = half_life(half_life_days)
    time_decay_weights = exponential_decay(days_since_watch, decay_rate)

    weights = rating_weights * time_decay_weights
    user_profile = np.average(watched_features, axis=0, weights=weights)

    return recommend_from_user_profile(user_profile, df, feature_matrix, top_k)
