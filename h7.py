import unittest
import sqlite3
import json
import os

# Name: Renee Du
# Who did you work with: Loria Sun

def readDataFromFile(filename):
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path, encoding = 'utf-8')
    file_data = f.read()
    f.close()
    json_data = json.loads(file_data)
    return json_data

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpTypesTable(data, cur, conn):
    type_list = []
    for pokemon in data:
        pokemon_type = pokemon['type'][0]
        if pokemon_type not in type_list:
            type_list.append(pokemon_type)
    cur.execute("CREATE TABLE IF NOT EXISTS Types (id INTEGER PRIMARY KEY, type TEXT UNIQUE)")
    for i in range(len(type_list)):
        cur.execute("INSERT OR IGNORE INTO Types (id,type) VALUES (?,?)",(i,type_list[i]))
    conn.commit()

## [TASK 1]: 20 points
# Finish the function setUpPokemonTable
# Iterate through the JSON data to get a list of pokemon
# Load all of the pokemon into a database table called Pokemon, with the following columns in each row:
# name (datatype: text and Primary key)
# type_id (datatype: integer)
# HP (datatype: integer)
# attack (datatype: integer)
# defense (datatype: integer)
# speed (datatype: integer)
# To find the type_id for each pokemon, you will have to look up the first type of each pokemon 
# in the types table we create for you. See setUpTypesTable for details.

def setUpPokemonTable(data, cur, conn):
    cur.execute("DROP TABLE IF EXISTS Pokemon")
    cur.execute("CREATE TABLE IF NOT EXISTS Pokemon (name TEXT PRIMARY KEY, type_id INTEGER,HP INTEGER,attack INTEGER,defense INTEGER,speed INTEGER)")
    count = 0
    for i in data:
        pokemon_type = i['type'][0]
        cur.execute("SELECT id FROM Types WHERE type = ?",(pokemon_type,))
        conn.commit() 
        type_id = int(cur.fetchone()[0])
        count += 1
        name = i['name']['english']
        hp = int(i['base']['HP'])
        attack = int(i['base']['Attack'])
        defense = int(i['base']['Defense'])
        speed = int(i['base']['Speed'])
        cur.execute("INSERT INTO Pokemon (name, type_id, HP, attack, defense, speed) VALUES (?,?,?,?,?,?)",
            (name, type_id, hp, attack, defense, speed)
        )
    conn.commit()

## [TASK 2]: 10 points
  # The function takes 3 arguments as input: an HP
  # the database cursor, and database connection object.  
  # It selects all the pokemon of a particular HP 
  # and returns a list of tuples. Each tuple contains 
  # the pokemon name, type_id and HP.

def getPokemonByHP(hp, cur, conn):
    cur.execute("SELECT name,type_id, HP FROM Pokemon WHERE HP=?", (hp,))
    conn.commit()
    lst = cur.fetchall()
    return lst

## [TASK 3]: 10 points
# The function takes 5 arguments as input: the HP,
# speed, and attack, the database cursor, and database connection object.
# It selects all the pokemon at the HP to the function 
# and at a speed greater than the rating passed to the function 
# and at an attack greater than the rating passed to the function. 
# The function returns a list of tuples.
# Each tuple in the list contains the pokemon name, speed, attack, and defense.

def getPokemonByHPAboveSpeedAndAboveAttack(HP, speed, attack, cur, conn):
    cur.execute("SELECT name, speed, attack, defense FROM pokemon WHERE HP = ? AND speed > ? AND attack > ?",(HP, speed, attack,))
    conn.commit()
    lst = cur.fetchall()
    return lst

## [TASK 4]: 15 points
# The function takes 5 arguments as input:a defense, a speed, a type, the database cursor,
# and database connection object. It selects all pokemon at a type 
# and at speed greater than the speed passed to the function,
# and at defense greater than the defense passed to the function.
# It returns a list of tuples, each tuple containing the
# pokemon name, type, speed, and defense.
# Note: You have to use JOIN for this task.

def getPokemonAboveSpeedAboveDefenseOfType(speed, defense, type, cur, conn):
    cur.execute("SELECT p.name, t.type, p.speed, p.defense FROM Pokemon p JOIN Types t ON p.type_id = t.id AND t.type = ? AND p.speed > ? AND p.defense > ?",(type,speed, defense,))
    conn.commit()
    lst = cur.fetchall()
    return lst


# [EXTRA CREDIT]
# This function takes in 5 parameters: type, attack, defense,
# the database cursor, and database connection object. It returns
# a list of all of the pokemon names that match the type, are
# greater than or equal to that attack, and match that defense.

def getPokemonOfType(type, attack, defense, cur, conn):
    cur.execute("SELECT p.name FROM Pokemon p JOIN Types t ON p.type_id = t.id AND t.type = ? AND p.attack >= ? AND p.defense = ?", (type, attack, defense,))
    conn.commit()
    lst = cur.fetchall()
    return lst



class TestAllMethods(unittest.TestCase):
    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.conn = sqlite3.connect(path+'/'+'pokemon.db')
        self.cur = self.conn.cursor()
        self.data = readDataFromFile('pokemon.txt')

    def test_pokemon_table(self):
        self.cur.execute('SELECT * from Pokemon')
        pokemon_list = self.cur.fetchall()
        self.assertEqual(len(pokemon_list), 106)
        self.assertEqual(len(pokemon_list[0]),6)
        self.assertIs(type(pokemon_list[0][0]), str)
        self.assertIs(type(pokemon_list[0][1]), int)
        self.assertIs(type(pokemon_list[0][2]), int)
        self.assertIs(type(pokemon_list[0][3]), int)
        self.assertIs(type(pokemon_list[0][4]), int)
        self.assertIs(type(pokemon_list[0][5]), int)


    def test_pokemon_by_hp(self):
        x = sorted(getPokemonByHP(50, self.cur, self.conn))
        self.assertEqual(len(x),8)
        self.assertEqual(len(x[0]), 3)
        self.assertEqual(x[0][0],"Cloyster")

        y = sorted(getPokemonByHP(30, self.cur, self.conn))
        self.assertEqual(len(y),6)
        self.assertEqual(y[2],('Krabby', 2, 30))
        self.assertEqual(y[4][2],30)
        self.assertEqual(y[5][1],2)

        z = sorted(getPokemonByHP(105, self.cur, self.conn))
        self.assertEqual(len(z),3)
        self.assertEqual(z[0][0],"Kangaskhan")
        self.assertEqual(z[2][2],105)
        self.assertEqual(len(getPokemonByHP(20, self.cur, self.conn)),0)

    def test_pokemon_by_hp_above_speed_above_attack(self):

        a = getPokemonByHPAboveSpeedAndAboveAttack(60, 30, 85, self.cur, self.conn)
        self.assertEqual(len(a),4)
        self.assertEqual(a[0][1],80)
        self.assertEqual(a[3][2],105)
        self.assertEqual(len(a[1]), 4)

        self.assertEqual(len(getPokemonByHPAboveSpeedAndAboveAttack(70, 40, 85, self.cur, self.conn)),0)

    def test_pokemon_above_speed_above_defense_of_type(self):
 
        b = sorted(getPokemonAboveSpeedAboveDefenseOfType(60, 60, "Fire", self.cur, self.conn))
        self.assertEqual(len(b), 2)
        self.assertEqual(type(b[0][0]), str)
        self.assertEqual(type(b[1][1]), str)
        self.assertEqual(len(b[1]), 4) 
        self.assertEqual(b[1], ('Ninetales', 'Fire', 100, 75)) 

        c = sorted(getPokemonAboveSpeedAboveDefenseOfType(60, 70, "Grass", self.cur, self.conn))
        self.assertEqual(len(c), 1)
        self.assertEqual(c, [('Venusaur', 'Grass', 80, 83)])
    
    def test_pokemon_of_type_extra_credit(self):
        e = sorted(getPokemonOfType("Ice", 45, 50, self.cur, self.conn))
        self.assertEqual(len(e), 1)

        f = getPokemonOfType("Grass", 70, 85, self.cur, self.conn)
        self.assertEqual(f, [('Vileplume',), ('Exeggutor',)])


def main():
    json_data = readDataFromFile('pokemon.txt')
    cur, conn = setUpDatabase('pokemon.db')
    setUpTypesTable(json_data, cur, conn)
    setUpPokemonTable(json_data, cur, conn)

    #### FEEL FREE TO USE THIS SPACE TO TEST OUT YOUR FUNCTIONS

    conn.close()



if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)
