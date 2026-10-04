import geopandas as gpd
from pathlib import Path

BASE_GRAPH_DIR = Path(__file__).parent / "graph"

gdf = gpd.read_file(
    BASE_GRAPH_DIR / "ban_do_hanh_chinh.geojson",
    columns=["ma_tinh", "ten_tinh", "geometry"],
)

simplified_gdf = gdf.copy(deep=True)
simplified_gdf["geometry"] = gdf["geometry"].simplify(
    tolerance=0.001, 
    preserve_topology=True
)

simplified_gdf.to_file(
    BASE_GRAPH_DIR / "ban_do_hanh_chinh_dashboard.gpkg", 
    driver = "GPKG"
)