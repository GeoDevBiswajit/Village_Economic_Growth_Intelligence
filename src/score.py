from sklearn.preprocessing import RobustScaler
from config import *

def calculate_scores(valid_growth_villages):
    print("Scaling and scoring features...")
    scaler = RobustScaler()
    
    features_to_scale = ['built_change', 'nightlight_density_change', 'total_population_change']
    scaled_features = [f"{f}_scaled" for f in features_to_scale]
    
    valid_growth_villages[scaled_features] = scaler.fit_transform(valid_growth_villages[features_to_scale])
    
    valid_growth_villages['economic_growth_score'] = (
        (valid_growth_villages['built_change_scaled'] * WEIGHT_BUILT) +
        (valid_growth_villages['nightlight_density_change_scaled'] * WEIGHT_LIGHTS) +
        (valid_growth_villages['total_population_change_scaled'] * WEIGHT_POP)
    )
    
    top_n_villages = valid_growth_villages.sort_values(by='economic_growth_score', ascending=False).head(TOP_N)
    print(f"Successfully identified the Top {TOP_N} economically growing villages.")
    
    return top_n_villages
