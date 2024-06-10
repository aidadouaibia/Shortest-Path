import osmnx as ox
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import csv
from geopy.geocoders import Nominatim
import streamlit as st
import folium
import heapq


def get_map_data():
    location = "Bejaia, Algeria"
    graph = ox.graph_from_place(location, network_type="drive")
    print("Graph created")
    return graph


def create_csv(sub_graph):
    csv_file = "Bejaia_regions.csv"
    geolocator = Nominatim(user_agent="my_geocoder", timeout=10)
    existing_place_names = set()

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Place Name", "Latitude", "Longitude"])

        for node_id in sub_graph.nodes:
            node_data = graph.nodes[node_id]
            latitude = node_data["y"]
            longitude = node_data["x"]
            location = geolocator.reverse((latitude, longitude), exactly_one=True)
            place_name = location.address if location else "Unknown"

            if place_name not in existing_place_names:
                if not place_name.isdigit() and not place_name.lower().startswith(('cw', 'rn', 'ru')):
                    writer.writerow([node_id, place_name, latitude, longitude])
                    existing_place_names.add(place_name)

    print(f"CSV file '{csv_file}' created successfully with node information.")
    return csv_file


def ucs(graph, source, target):
    frontier = [(0, source)]
    explored = set()
    came_from = {source: None}
    path_cost = {source: 0}

    while frontier:
        cost, current_node = heapq.heappop(frontier)

        if current_node in explored:
            continue

        explored.add(current_node)

        if current_node == target:
            break

        for neighbor in graph.neighbors(current_node):
            edge_weight = graph[current_node][neighbor][0]['length']
            new_cost = cost + edge_weight

            if neighbor not in path_cost or new_cost < path_cost[neighbor]:
                path_cost[neighbor] = new_cost
                priority = new_cost
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current_node

    path = []
    while current_node is not None:
        path.append(current_node)
        current_node = came_from[current_node]
    path.reverse()

    return path


def main():
    global graph
    global map
    global df
    graph = get_map_data()

    df = pd.read_csv("Bejaia_regions.csv")

    st.title("Shortest Path Finder")

    source = st.selectbox("Select Source Place", df['Place Name'].tolist())
    destination = st.selectbox("Select Destination Place", df['Place Name'].tolist())

    color_list = []
    size_list = []

    for item in df['Place Name'].values:
        if item == source or item == destination:
            color_list.append('#008000')
            size_list.append(50)
        else:
            color_list.append('#FF0000')
            size_list.append(1)

    df['color'] = color_list
    df['size'] = size_list

    if st.button('Find Shortest Path'):
        if source != destination:
            src = df[df['Place Name'] == source]['ID'].values[0]
            dest = df[df['Place Name'] == destination]['ID'].values[0]
            shortest_path = ucs(graph, src, dest)
            print(shortest_path)

            fig, ax = ox.plot_graph_route(
                graph,
                shortest_path,
                route_color='r',
                route_linewidth=3,
                node_size=0,
                figsize=(15, 15),
                show=False,
                close=False
            )
            figure = fig
            st.pyplot(fig=figure)


if __name__ == "__main__":
    main()
