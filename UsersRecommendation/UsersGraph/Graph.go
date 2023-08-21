package main

import (
	
)

// represents users as an undirected weighted graph
type UserGraph struct {
	capacity int; // the maximum number of nodes allowed in the graph
	size int; // the number of current nodes in the graph
	adjacencyList []*User_GraphNode; // an adjacency linked list of each node
}

// some function to created an undirected weighted user graph network
func NewUserGraph(capacity int) *UserGraph {
	return &UserGraph{
		capacity: capacity,
		size: 0,
		adjacencyList: make([]*User_GraphNode, capacity),
	}
}

// function to add edge between 2 graph nodes in the graph -> void
func AddEdges(from_User_id string, to_User_id string) {
	
}	

