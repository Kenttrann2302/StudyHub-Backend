package main

import (
	"github.com/google/uuid"
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
func (g *UserGraph) AddEdges(from_User_node_key int16, to_User_node_key int16, user_id_from uuid.UUID, username_from string, user_info_from *User_Information, user_address_from *User_Address, user_study_pref_from *User_Study_Preferences, availability_time_from *AvailabilityTime, user_id_to uuid.UUID, username_to string, user_info_to *User_Information, user_address_to *User_Address, user_study_pref_to *User_Study_Preferences, availability_time_to *AvailabilityTime) {
	// add the edge from to to
	from_temp := g.adjacencyList[from_User_node_key];
	if from_temp == nil {
		g.adjacencyList[from_User_node_key] = NewUserGraphNode(to_User_node_key, user_id_to, username_to, user_info_to, user_address_to, user_study_pref_to, availability_time_to);
	} // if there is no from node yet then create one

	for from_temp.next != nil {
		from_temp = from_temp.next;
	}

	// Create new node to the list
	from_temp.next = NewUserGraphNode(to_User_node_key, user_id_to, username_to, user_info_to, user_address_to, user_study_pref_to, availability_time_to);

	// add the edge to to from
	to_temp := g.adjacencyList[to_User_node_key];
	if to_temp == nil {
		g.adjacencyList[to_User_node_key] = NewUserGraphNode(from_User_node_key, user_id_from, username_from, user_info_from, user_address_from, user_study_pref_from, availability_time_from);
	} // if there is no to node yet then create a new one
	
	for to_temp.next != nil {
		to_temp = to_temp.next;
	}

	// Create a new node
	to_temp.next = NewUserGraphNode(from_User_node_key, user_id_from, username_from, user_info_from, user_address_from, user_study_pref_from, availability_time_from);
}	

// function to assign weight for each edge on the graph
func (g *UserGraph) AssignWeight(from_User_node_key int16, to_User_node_key int16) {
	
}

// function to start a bfs traversal on the graph

