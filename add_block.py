#!/usr/bin/env python3
"""
Block addition module for FGDB (Folder Graph Database)
This module adds new nodes to the graph based on block folder data.
"""

import networkx as nx
import matplotlib.pyplot as plt
import pickle
import json
import os
import sys
import argparse


class BlockAdder:
    """Manages adding blocks to the graph and visualization."""
    
    def __init__(self, graph_file="graph.pickle"):
        """
        Initialize BlockAdder with specified graph file.
        
        Args:
            graph_file (str): Path to the graph pickle file
        """
        self.graph_file = graph_file
        self.graph = None
    
    def load_graph(self):
        """
        Load the graph from pickle file.
        
        Returns:
            bool: True if load successful, False otherwise
        """
        try:
            if os.path.exists(self.graph_file):
                with open(self.graph_file, 'rb') as f:
                    self.graph = pickle.load(f)
                print(f"Graph loaded from {self.graph_file}")
                return True
            else:
                print(f"Error: Graph file {self.graph_file} does not exist.")
                print("Please run init.py first to create the initial graph.")
                return False
        except Exception as e:
            print(f"Error loading graph: {e}")
            return False
    
    def save_graph(self):
        """
        Save the current graph to pickle file.
        """
        try:
            with open(self.graph_file, 'wb') as f:
                pickle.dump(self.graph, f)
            print(f"Graph saved to {self.graph_file}")
        except Exception as e:
            print(f"Error saving graph: {e}")
    
    def read_block_data(self, block_folder):
        """
        Read data.json from the specified block folder.
        
        Args:
            block_folder (str): Path to the block folder containing data.json
            
        Returns:
            dict: Block data if successful, None otherwise
        """
        data_file = os.path.join(block_folder, "data.json")
        
        if not os.path.exists(data_file):
            print(f"Error: data.json not found in {block_folder}")
            return None
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Block data loaded from {data_file}")
            return data
        except Exception as e:
            print(f"Error reading data.json: {e}")
            return None
    
    def add_node_to_graph(self, block_data, block_folder):
        """
        Create new node and add it to the graph.
        
        Args:
            block_data (dict): Data from data.json
            block_folder (str): Path to the block folder
        """
        # Generate unique node ID based on folder path
        node_id = os.path.basename(os.path.abspath(block_folder))
        
        # Add full_path to block_data
        block_data["full_path"] = os.path.abspath(block_folder)
        
        # Add node to graph
        self.graph.add_node(node_id, **block_data)
        
        # Connect to root node (you can modify this logic as needed)
        if node_id != "root":
            self.graph.add_edge("root", node_id)
        
        print(f"Node '{node_id}' added to graph with attributes:")
        for key, value in block_data.items():
            print(f"  {key}: {value}")
    
    def visualize_graph(self):
        """
        Visualize the graph with different shapes based on node categories.
        """
        if self.graph is None or self.graph.number_of_nodes() == 0:
            print("No graph to visualize.")
            return
        
        plt.figure(figsize=(12, 8))
        
        # Get node positions using spring layout
        pos = nx.spring_layout(self.graph, seed=42)
        
        # Separate nodes by category for different styling
        root_nodes = []
        data_nodes = []
        function_nodes = []
        other_nodes = []
        
        for node in self.graph.nodes():
            category = self.graph.nodes[node].get('category', 'other')
            if category == 'root':
                root_nodes.append(node)
            elif category == 'data':
                data_nodes.append(node)
            elif category == 'function':
                function_nodes.append(node)
            else:
                other_nodes.append(node)
        
        # Draw nodes with different shapes
        # Root nodes - diamond shape (using 'D' marker)
        if root_nodes:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=root_nodes, 
                                 node_color='red', node_shape='D', 
                                 node_size=800, alpha=0.8, label='Root')
        
        # Data nodes - circle shape (default 'o' marker)
        if data_nodes:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=data_nodes, 
                                 node_color='blue', node_shape='o', 
                                 node_size=600, alpha=0.8, label='Data')
        
        # Function nodes - rectangle shape (using 's' marker for square)
        if function_nodes:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=function_nodes, 
                                 node_color='green', node_shape='s', 
                                 node_size=700, alpha=0.8, label='Function')
        
        # Other nodes - default circle
        if other_nodes:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=other_nodes, 
                                 node_color='gray', node_shape='o', 
                                 node_size=500, alpha=0.8, label='Other')
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, alpha=0.5, arrows=True, 
                             arrowsize=20, edge_color='gray')
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, pos, font_size=10, font_weight='bold')
        
        # Add legend
        plt.legend(scatterpoints=1, loc='upper right')
        
        # Set title and layout
        plt.title("FGDB Graph Visualization", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        # Show the plot
        plt.show()
        
        print("Graph visualization displayed.")
        print(f"Total nodes: {self.graph.number_of_nodes()}")
        print(f"Total edges: {self.graph.number_of_edges()}")


def main():
    """
    Main function to execute block addition process.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Add block to FGDB graph')
    parser.add_argument('block_folder', help='Path to the block folder containing data.json')
    
    args = parser.parse_args()
    block_folder = args.block_folder
    
    print("=== FGDB Block Addition ===")
    print(f"Target block folder: {block_folder}")
    
    # Validate block folder exists
    if not os.path.exists(block_folder):
        print(f"Error: Block folder '{block_folder}' does not exist.")
        sys.exit(1)
    
    # Create BlockAdder instance
    adder = BlockAdder()
    
    # Load existing graph
    if not adder.load_graph():
        sys.exit(1)
    
    # Read block data from data.json
    block_data = adder.read_block_data(block_folder)
    if block_data is None:
        sys.exit(1)
    
    # Add node to graph
    adder.add_node_to_graph(block_data, block_folder)
    
    # Save updated graph
    adder.save_graph()
    
    # Visualize the graph
    adder.visualize_graph()
    
    print("=== Block Addition Complete ===")


if __name__ == "__main__":
    main()
