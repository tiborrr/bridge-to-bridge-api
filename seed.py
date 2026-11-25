import os
import sys

# Add src to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from bridge_to_bridge_api.core.database import get_session_local, Base, get_engine
from bridge_to_bridge_api.models.trajectory import Trajectory

def seed():
    Base.metadata.create_all(bind=get_engine())
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    if db.query(Trajectory).count() == 0:
        # 1. Spoorbrug -> Wilhelminabrug (North to South)
        t1 = Trajectory(
            name="Spoorbrug naar Wilhelminabrug",
            start_bridge_name="Spoorbrug",
            start_north_lat=52.255876,
            start_north_lng=6.146477,
            start_south_lat=52.255026,
            start_south_lng=6.145213,
            start_direction="northToSouth",
            finish_bridge_name="Wilhelminabrug",
            finish_north_lat=52.24968536814231,
            finish_north_lng=6.158249956613249,
            finish_south_lat=52.24843984912324,
            finish_south_lng=6.157123369214389,
            finish_direction="northToSouth"
        )
        
        # 2. Wilhelminabrug -> Spoorbrug (South to North)
        t2 = Trajectory(
            name="Wilhelminabrug naar Spoorbrug",
            start_bridge_name="Wilhelminabrug",
            start_north_lat=52.24968536814231,
            start_north_lng=6.158249956613249,
            start_south_lat=52.24843984912324,
            start_south_lng=6.157123369214389,
            start_direction="southToNorth",
            finish_bridge_name="Spoorbrug",
            finish_north_lat=52.255876,
            finish_north_lng=6.146477,
            finish_south_lat=52.255026,
            finish_south_lng=6.145213,
            finish_direction="southToNorth"
        )
        
        db.add_all([t1, t2])
        db.commit()
        print("Database seeded with default trajectories.")
    else:
        print("Trajectories already exist in database.")
    
    db.close()

if __name__ == "__main__":
    seed()
