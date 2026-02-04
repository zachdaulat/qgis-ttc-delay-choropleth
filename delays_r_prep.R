pak::pak("qs2")
pak::pak("sf")

library(sf)
library(qs2)
library(dplyr)
library(lobstr)

delays <- qd_read("data/delays_policies.qdata", nthreads = 8) |>
  st_as_sf()

class(delays$geometry)

delays_qgis <- delays |>
  select(geometry) |>
  filter(!st_is_empty(geometry))


# Checking for invalid geometries
sum(!st_is_valid(delays_qgis))

# # Fixing any invalid geometries if they exist
# delays_qgis <- st_make_valid(delays_qgis)

st_crs(delays_qgis)


st_write(
  delays_qgis,
  "data/delays_qgis.gpkg",
  layer = "delays",
  driver = "GPKG",
  delete_layer = TRUE,
  delete_dsn = TRUE
)
