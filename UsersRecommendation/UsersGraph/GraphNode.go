package main

// create a class node to represent each user 
import (
	"github.com/google/uuid"
)

// user information object
type User_Information struct {
	Interests string
	Activity_status bool
	Age int16
	Education_institutions string
	Education_majors string
	Education_degrees string
	Graduation_date string
}

// user's address object
type User_Address struct {
	Address_line_1 string
	Address_line_2 string
	City string
	Province string
	Country string
	Postal_code string
	Timezone string
}

// user's study preferences object
type User_Study_Preferences struct {
	Study_env_pref string
	Study_time_pref string
	Time_management_pref string
	Study_techniques_pref string
	Courses_pref string
	Communication_pref string
}

// availability schedule object
type AvailabilityTime struct {
	Availability_time string
}

// create a struct type Node to represent each user
type User_GraphNode struct {
	// user identifier
	User_node_key int16 // each user will be assigned an integer key to specified the index of the node in the graph
	user_id uuid.UUID
	username string

	// user information
	user_information User_Information

	// user's address
	user_address User_Address
	
	// study preferences
	user_study_pref User_Study_Preferences

	// availability schedule
	availability_time AvailabilityTime

	// Node members
	next *User_GraphNode
}

func NewUserInformation(Interests_in string, Activity_status_in bool, Age_in int16, Education_institutions_in string, Education_majors_in string, Education_degrees_in string, Graduation_date_in string) *User_Information {
	return &User_Information{
		Interests: Interests_in,
		Activity_status: Activity_status_in,
		Age: Age_in,
		Education_institutions: Education_institutions_in,
		Education_majors: Education_majors_in,
		Education_degrees: Education_degrees_in,
		Graduation_date: Graduation_date_in,
	}
}

func NewUserAddress(Address_line_1_in string, Address_line_2_in string, City_in string, Province_in string, Country_in string, Postal_code_in string, Timezone_in string) *User_Address {
	return &User_Address{
		Address_line_1: Address_line_1_in,
		Address_line_2: Address_line_2_in,
		City: City_in,
		Province: Province_in,
		Country: Country_in,
		Postal_code: Postal_code_in,
		Timezone: Timezone_in,
	}
}

func NewUserStudyPreferences(Study_env_pref_in string, Study_time_pref_in string, Time_management_pref_in string, Study_techniques_pref_in string, Courses_pref_in string, Communication_pref_in string) *User_Study_Preferences {
	return &User_Study_Preferences{
		Study_env_pref: Study_env_pref_in,
		Study_time_pref: Study_time_pref_in,
		Time_management_pref: Time_management_pref_in,
		Study_techniques_pref: Study_techniques_pref_in,
		Courses_pref: Courses_pref_in,
		Communication_pref: Communication_pref_in,
	}
}

func NewAvailabilityTime(AvailabilityTime_in string) *AvailabilityTime {
	return &AvailabilityTime{
		Availability_time: AvailabilityTime_in,
	}
}

func NewUserGraphNode(User_node_key_in int16, user_id_in uuid.UUID, username_in string, user_info *User_Information, user_address *User_Address, user_study_pref *User_Study_Preferences, availability_time *AvailabilityTime) *User_GraphNode {
	return &User_GraphNode{
		User_node_key: User_node_key_in,
		user_id: user_id_in,
		username: username_in,
		user_information: *user_info,
		user_address: *user_address,
		user_study_pref: *user_study_pref,
		availability_time: *availability_time,
		next: nil,
	}
}



