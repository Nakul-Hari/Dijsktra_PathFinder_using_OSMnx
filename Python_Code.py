import os
import networkx as nx
import plotly.graph_objects as go
import osmnx as ox
import numpy as np

def dijkstra_shortest_path(start_node, end_node, road_graph):
    # Initialize dictionaries to store distances and predecessors
    distances = {node: float('inf') for node in road_graph.nodes}
    predecessors = {node: None for node in road_graph.nodes}

    distances[start_node] = 0   # Intial node distance = 0
    visited = set()  # Stores visited nodes

    # Dijkstra Algorithmn implementation
    while len(visited) < len(road_graph.nodes):
        # Find the node with the minimum distance among unvisited nodes
        min_dist = float('inf')
        min_node = None
        for node in road_graph.nodes:
            if node not in visited and distances[node] < min_dist:
                min_dist = distances[node]
                min_node = node

        visited.add(min_node)   # Minimum visited node is set as visited

        if min_node == end_node: # Break if end_node is reached
            break

        # Update distances and predecessors for neighboring nodes
        for neighbor, attr in road_graph[min_node].items():
            edge_weight = attr[0].get('length', 1.0)   # Use edge length as weight
            new_dist = distances[min_node] + edge_weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = min_node

    # Reconstruct the shortest path
    path = []
    current_node = end_node
    while current_node is not None:
        path.insert(0, current_node)
        current_node = predecessors[current_node]

    return path

def calculate_nearest_node(graph, latitude, longitude): 

    target_coords = np.array([[longitude, latitude]])     # Converting latitude and longitude to 2D array
    node_coords = np.array([[data['x'], data['y']] for _, data in graph.nodes(data=True)])  # Extractin Node cordinates
    distances = np.linalg.norm(target_coords - node_coords, axis=1) # Calculating euclidan distance
    nearest_node_index = np.argmin(distances)  # Getting the nearest node
    nearest_node = list(graph.nodes())[nearest_node_index] # retrieving the nearest node identifier

    return nearest_node

def generate_path(origin_point, target_point, perimeter):

    # Getting the boundary of the path by splicing the origin_point and target_point
    origin_lat = origin_point[0]
    origin_long = origin_point[1]

    target_lat = target_point[0]
    target_long = target_point[1]
    
    if  origin_lat > target_lat:
        north = origin_lat 
        south = target_lat
    else:
      north = target_lat
      south = origin_lat

    if  origin_long > target_long:
        east = origin_long 
        west = target_long
    else:
      east = target_long
      west = origin_long

    mode = 'drive' # Modes 'drive', 'bike', 'walk' (walk is usually too slow)

    roadgraph = ox.graph_from_bbox(north+perimeter, south-perimeter, east+perimeter, west-perimeter, network_type = mode, simplify=False )

    origin_node = calculate_nearest_node(roadgraph, origin_point[0], origin_point[1]) #calculating nearest noed from function

    target_node = calculate_nearest_node(roadgraph, target_point[0], target_point[1])
    
    # This is the inbuild dijkstras function
    #route = nx.shortest_path(roadgraph, origin_node, target_node, weight = 'length', method='dijkstra')
    route = dijkstra_shortest_path(origin_node, target_node, roadgraph)

    lat = []
    long = []

    for i in route:
        point = roadgraph.nodes[i]
        long.append(point['x'])
        lat.append(point['y'])
    
    return long, lat
   
def plot_map(origin_point, target_point, long, lat):
    print(origin_point) 
    print(target_point) 
    print(long) 
    print(lat) 

    print("Setting up figure...")  
    fig = go.Figure(go.Scattermapbox(
        name = "Origin",
        mode = "markers",
        lon = [origin_point[1]],
        lat = [origin_point[0]],
        marker = {'size': 16, 'color':'#CE55FF'},
        )   
    )

    print("Generating paths...")   # Plotting the path
    for i in range(len(lat)):
        fig.add_trace(go.Scattermapbox(
            name = "Path",
            mode = "lines",
            lon = long[i],
            lat = lat[i],
            marker = {'size': 10},
            showlegend=False,
            line = dict(width = 4.5, color = '#CE55FF'))
            
        )


    print("Generating target...")      # Plot the target geocoordinates to the map
    fig.add_trace(go.Scattermapbox(
        name = "Destination",
        mode = "markers",
        showlegend=False,
        lon = [target_point[1]],
        lat = [target_point[0]],
        marker = {'size': 16, 'color':'#CE55FF'}))

    # Style the map layout
    fig.update_layout(
        mapbox_style="light", 
        mapbox_accesstoken="", #Upload your access token here
        legend=dict(yanchor="top", y=1, xanchor="left", x=0.83), #x 0.9
        title="<span style='font-size: 32px;'><b>The Shortest Paths Dijkstra Map</b></span>",
        font_family="Times New Roman",
        font_color="#333333",
        title_font_size = 32,
        font_size = 18,
        width=1000, #2000
        height=1000,
    )

    # Set the center of the map
    lat_center = (origin_point[0] + target_point[0])/2
    long_center = (origin_point[1] + target_point[1])/2

    # Add the center to the map layout
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
        title=dict(yanchor="top", y=.97, xanchor="left", x=0.03), #x 0.75
        mapbox = {
            'center': {'lat': lat_center, 
            'lon': long_center},
            'zoom': 12.2}
    )

    # Save map in output folder
    print("Saving image to output folder...");
    fig.write_image(OS_PATH + '/output/dijkstra_map.jpg', scale=3)
    # Show the map in the web browser
    print("Generating map in browser...");

    fig.show()


# Code starts here 

OS_PATH = os.path.dirname(os.path.realpath('file'))
print(OS_PATH)

origin_input = input("Enter the origin geocoordinate (latitude, longitude): ")
target_input = input("Enter the target geocoordinate (latitude, longitude): ")

origin_coordinates = origin_input.replace("(", "").replace(")", "").split(",")
target_coordinates = target_input.replace("(", "").replace(")", "").split(",")

origin_latitude = float(origin_coordinates[0].strip())
origin_longitude = float(origin_coordinates[1].strip())
target_latitude = float(target_coordinates[0].strip())
target_longitude = float(target_coordinates[1].strip())

origin_point = (origin_latitude, origin_longitude)
target_point = (target_latitude, target_longitude)

print("Origin Point:", origin_point)
print("Target Point:", target_point)

long = []
lat = []

perimeter = 0.10 # Perimeter is the boundary of the roadmap

print("* * * * * * * * * * * * * Finding Optimal Path * * * * * * * * * * * * * *")
x, y = generate_path(origin_point, target_point, perimeter)
    
long.append(x)
lat.append(y)

plot_map(origin_point, target_point, long, lat)
