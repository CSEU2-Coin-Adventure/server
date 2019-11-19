import pymongo
import requests
import time
import json

from pymongo import MongoClient

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value):
        self.stack.insert(0, value)

    def pop(self):
        if self.length():
            return self.stack.pop(0)
        else:
            return None

    def length(self):
        return len(self.stack)

class Traverse:
    def __init__(self):
        self.path = []
        self.current_room = None
        self.stack = None
        self.hansel_stack = None
        self.direction_stack = None
        self.visited = visited or {}
        self.rooms = {}
        self.previous_room = None

        self.post = None

        self.opposites = {
            'n': 's',
            'e': 'w',
            's': 'n',
            'w': 'e'
        }

    def init(self):
        self.init_db()
        self.stack = Stack()
        self.hansel_stack = Stack()
        self.direction_stack = Stack()
        self.get_visited()
        self.init_current_room()

    def init_db(self):
        client = MongoClient(
            "mongodb://mattshardman:mappymap12@ds039211.mlab.com:39211/cs_map_project?retryWrites=false")
        db = client.cs_map_project
        self.posts = db.rooms

    def get_visited(self):
        with open("visited.json", "r") as f:
            self.visited = json.loads(f.read())

    def init_current_room(self):
        room = requests.get("https://lambda-treasure-hunt.herokuapp.com/api/adv/init/", headers={
                            'Authorization': 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c'}).json()
        self.current_room = room
        self.save_to_db(room)
        self.stack.push(room)
        time.sleep(room.get('cooldown'))

    def save_to_db(self, room):
        result = self.posts.insert_one(room)
        print('One post: {0}'.format(result.inserted_id))

    def move(self, direction):
        new_room = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/move/", json={
            'direction': direction}, headers={'Authorization': 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c'}).json()
        return new_room

    def get_treasure(self):
        treasure = requests.post("https://lambda-treasure-hunt.herokuapp.com/api/adv/take/", json={
                                 'name': 'treasure'}, headers={'Authorization': 'Token 91eab72c1255c3828263a3a60a6cefc409f6461c'}).json()
        print(treasure)
        time.sleep(20)

    def save_new_room(self, room):
        # create exits array
        exits = room.get('exits')
        room_exits = {}
        for r in exits:
            room_exits[r] = '?'
        # store response in dict (for now) with room_id as key and all info as value
        self.visited[room.get('room_id')] = room_exits
        # save visited to json
        self.save_file(self.visited, "visited.json")

    def append_room(self, direction_from):
        # add item to visited array with exists as value room number as key
        self.path.append(direction_from)
        self.save_file(self.path, "path.txt")
        self.hansel_stack.push(
            (self.opposites[direction_from], self.previous_room))
        # set direction to previous room number for current room
        self.visited[room.get(
            'room_id')][self.opposites[direction_from]] = self.previous_room
        self.visited[previous_room][direction_from] = room.get(
            'room_id')
        self.save_file(self.visited, "visited.json")

    def check_exits(self, room):
            # loop through exits array on item
        for (d, i) in self.visited[room.get('room_id')].items():
            # if unexplored add to stack
            if i == '?':
                # call the api with each of the directions
                new_room = move(d)
                print(new_room)

                time.sleep(new_room.get('cooldown'))

                if 'tiny treasure' in new_room.get('items'):
                    self.get_treasure()

                print(new_room.get('errors'))
                if len(new_room.get('errors')):
                    time.sleep(20)

                self.save_to_db(new_room)

                # add room to stack
                self.stack.push(new_room)
                self.direction_stack.push(d)
                break

    def save_file(self, item, filename):
        # save visited to file
        with open(filename, 'w') as outfile:
            json.dump(item, outfile)

    def explore(self):
        # pop the stack and set to room
        room = self.stack.pop()
        self.rooms[room.get('room_id')] = room
        # pop direction stack
        direction_from = self.direction_stack.pop()
        # if the room has not been visited before or
        if room.get('room_id') not in self.visited or '?' in self.visited[room.get('room_id')].values():
            # if room number is not already in rooms add it
            if room.get('room_id') not in self.visited:
                self.save_new_room(room)
            # add direction to path array and opposite to hansel stack also add room number that goes with that direction to stack
            if direction_from != None and self.previous_room != None:
                self.append_room(direction_from)

            self.check_exits(room)

            self.previous_room = room.get('room_id')

    def backtrack(self):
        (d, r) = self.hansel_stack.pop()
        print("return_direction", d, "return room", r)
        # go in direction of hansel_stack
        new_room = self.move(d)

        print(new_room)
        if len(new_room.get('errors')):
            time.sleep(20)

        time.sleep(new_room.get('cooldown'))
        # add direction to path
        self.path.append(d)
        self.save_file(self.path, "path.txt")
        # push new_room on to stack
        self.stack.push(new_room)

    def run(self):
        while self.stack.length() or self.hansel_stack.length():
            if self.stack.length():
                self.explore()
            else:
                self.backtrack()

        return self.visited

traverser = Traverse()
traverser.init()
traverser.run()