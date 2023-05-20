<a id="DatabaseManagement"></a>

# DatabaseManagement

Big Brother Database Mangement Class

Manages Database Requests
can Import and Export Pictures from Database

@Author: Julian Flieller <@Dr.Hype#0001>
@Date:   2023-05-13
@Project: ODS-Praktikum-Big-Brother
@Filename: new_database_management.py
@Last modified by:   Julian FLieller
@Last modified time: 2023-05-19

<a id="DatabaseManagement.np"></a>

## np

<a id="DatabaseManagement.pickle"></a>

## pickle

<a id="DatabaseManagement.uuid"></a>

## uuid

<a id="DatabaseManagement.dt"></a>

## dt

<a id="DatabaseManagement.timezone"></a>

## timezone

<a id="DatabaseManagement.pymongo"></a>

## pymongo

<a id="DatabaseManagement.BBDB"></a>

## BBDB Objects

```python
class BBDB()
```

Database Baseclass
Subclasses like wire_DB inherit methods and Varaibles
This is done to reduce Code and to Unify the usage of the Database

<a id="DatabaseManagement.BBDB.__init__"></a>

#### \_\_init\_\_

```python
def __init__(dbhost: str = None, username: str = None, password: str = None)
```

Builds up the initial connection to the database

<a id="DatabaseManagement.BBDB.close"></a>

#### close

```python
def close()
```

Close the connection with the database

<a id="DatabaseManagement.BBDB.commit"></a>

#### commit

```python
def commit()
```

not needed for mongodb

<a id="DatabaseManagement.BBDB.delUser"></a>

#### delUser

```python
def delUser(**kwargs) -> bool
```

Delete a user from the database with the given uuid or username

Keyword arguments: Only one of the keyword arguments should 
be set. Otherwise an error will be returned.  
user_uuid -- ID of the user that you want to delete.  
username  -- Username of the user that you want to delete.

<a id="DatabaseManagement.BBDB.addAdminRelation"></a>

#### addAdminRelation

```python
def addAdminRelation(admin_uuid, child_uuid)
```

Add a user as an admin with the given child_uuid aka user_uuid

**Arguments**:

- `admin_uuid` - This variable is depricated and isn't really used.
- `child_uuid` - This is the user_id of the user that should be made admin.

<a id="DatabaseManagement.BBDB.get_username"></a>

#### get\_username

```python
def get_username(uuids: list)
```

Fetches usernames from database belonging to the given uuids

**Arguments**:

- `uuids` - This is a list of user_uuid. Those are the uuids of which you want to get the usernames.
  

**Returns**:

  Returns the a list of usernames that correspond to the user_uuid
  that have been inputted. The index i of the return list corresponds
  to uuids[i] in the input.

<a id="DatabaseManagement.BBDB.login_user"></a>

#### login\_user

```python
def login_user(**kwargs)
```

Creates a new entry in the login_table for the user with the given uuid or username.

Keyword arguments: Only one of the keyword arguments should be set. Otherwise an error will be returned.
user_uuid -- ID of the user that you want to delete.
username  -- Username of the user that you want to delete.

**Returns**:

  Returns (False,False) if the login fails and the timestamp of the
  login if it succeeds.

<a id="DatabaseManagement.BBDB.update_login"></a>

#### update\_login

```python
def update_login(**kwargs)
```

Updates the status of the login of one user with a certain 
user_uuid or username.

Keyword arguments:
user_id -- ID of the user of which you want to log in. You can only set 
either the user_id or the username otherwise you are going to get an error.
username -- Username of the user which you want to log in. You can only
set either the user_id or the username otherwise you are going to get an error.
time -- The timestamp of the login you want to update.

<a id="DatabaseManagement.BBDB.register_user"></a>

#### register\_user

```python
def register_user(username: str)
```

Creates a new user in the database with the given username.

**Arguments**:

- `username` - The username of the new user.
  

**Returns**:

  If the user has been successfully registered then it returns the
  user_uuid of the user what has been created.
  
  Exception:
  Raises an exception if the username already exists.

<a id="DatabaseManagement.BBDB.getUsers"></a>

#### getUsers

```python
def getUsers(limit=-1)
```

Fetches all Users with their uuids and usernames from the database

Optional arguments:
limit -- This argument sets the amount of users that you want to limit
your request to. If it's set to a negative number (which it is by default),
then the search isn't limited.

**Returns**:

  If `limit` is negative then it returns a dictionary of all users and the
  associated usernames. If the limit is non-negative then it returns a
  list wiht `limit` amount of entries. The dictionary key are the user_uuid
  and the value is the username.

<a id="DatabaseManagement.BBDB.getUserWithId"></a>

#### getUserWithId

```python
def getUserWithId(user_uuid)
```

Returns the username corresponding to the user_uuid.

**Arguments**:

- `user_uuid` - The user_uuid.
  

**Returns**:

  Returns the username corresponding to the user_uuid. If the user with the
  given ID doesn't exist then None gets returned.

<a id="DatabaseManagement.BBDB.deleteUserWithId"></a>

#### deleteUserWithId

```python
def deleteUserWithId(user_uuid)
```

Deletes the user with the given user_uuid from the database.

**Arguments**:

- `user_uuid` - ID of the user that should be deleted.
  

**Returns**:

  Returns True if the user has been successfully deleted. And
  False otherwise (e.g. user didn't exist in the database).

<a id="DatabaseManagement.BBDB.getUser"></a>

#### getUser

```python
def getUser(username)
```

Returns the uuid corresponding to the username.

**Arguments**:

- `username` - The username of the user.
  

**Returns**:

  Returns the uuid corresponding to the username. If the username
  doesn't exist then it returns None.

<a id="DatabaseManagement.BBDB.insertPicture"></a>

#### insertPicture

```python
def insertPicture(pic: np.ndarray, user_uuid: uuid.UUID)
```

<a id="DatabaseManagement.BBDB.getPicture"></a>

#### getPicture

```python
def getPicture(query: str)
```

<a id="DatabaseManagement.BBDB.closeGraceful"></a>

#### closeGraceful

```python
def closeGraceful()
```

Should be called everytime the Program Shuts down so that the Server
Doesnt overflow with psql processes
This includes all Exceptions

<a id="DatabaseManagement.wire_DB"></a>

## wire\_DB Objects

```python
class wire_DB(BBDB)
```

Subclass from BBDB
Inherits Methods and Variables

<a id="DatabaseManagement.wire_DB.__init__"></a>

#### \_\_init\_\_

```python
def __init__(dbhost: str = None)
```

<a id="DatabaseManagement.wire_DB.insertTrainingPicture"></a>

#### insertTrainingPicture

```python
def insertTrainingPicture(pic: np.ndarray, user_uuid: uuid.UUID)
```

Inserts a new training picture into the database and returns the
uuid of the inserted picture.

**Arguments**:

- `pic` - Picture to be inserted into the database.
- `user_uuid` - ID of the user which owns the picture.
  

**Returns**:

  Returns the uuid of the picture that has been inserted into the database.
  
  Exception:
- `TypeError` - Gets risen if the type of the input isn't the expected type.

<a id="DatabaseManagement.wire_DB.getTrainingPictures"></a>

#### getTrainingPictures

```python
def getTrainingPictures(where: str)
```

Returns training pictures from the database with the given where clause

<a id="DatabaseManagement.wire_DB.getAllTrainingsImages"></a>

#### getAllTrainingsImages

```python
def getAllTrainingsImages()
```

Returns all training images from the database in three lists: 
pics, uuids, user_uuids

<a id="DatabaseManagement.opencv_DB"></a>

## opencv\_DB Objects

```python
class opencv_DB(BBDB)
```

<a id="DatabaseManagement.opencv_DB.__init__"></a>

#### \_\_init\_\_

```python
def __init__(dbhost: str = None)
```

<a id="DatabaseManagement.frontend_DB"></a>

## frontend\_DB Objects

```python
class frontend_DB(BBDB)
```

<a id="DatabaseManagement.frontend_DB.__init__"></a>

#### \_\_init\_\_

```python
def __init__(dbhost: str = None)
```

<a id="DatabaseManagement.UsernameExists"></a>

## UsernameExists Objects

```python
class UsernameExists(Exception)
```

<a id="DatabaseManagement.makeSuperAdmin"></a>

#### makeSuperAdmin

```python
def makeSuperAdmin(name)
```

<a id="DatabaseManagement.delThisUser"></a>

#### delThisUser

```python
def delThisUser(name)
```

