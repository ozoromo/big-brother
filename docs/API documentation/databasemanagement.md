<a id="DatabaseManagement"></a>

# DatabaseManagement

Big Brother Database Mangement Class

Manages Database Requests
can Import and Export Pictures from Database

@Author: Julian Flieller <@Dr.Hype#0001>
@Date:   2023-05-13
@Project: ODS-Praktikum-Big-Brother
@Filename: new_database_management.py
@Last modified by:   Julian Flieller
@Last modified time: 2023-06-16

<a id="DatabaseManagement.BBDB"></a>

## BBDB Objects

```python
class BBDB()
```

Database Baseclass

<a id="DatabaseManagement.BBDB.__init__"></a>

#### \_\_init\_\_

```python
def __init__(mongo_client=None)
```

Builds up the initial connection to the database

Optional Arguments:
mongo_client -- In case you are using a different mongo cluster.
We also offer a default mongo cluster that you can use. In case you
use a different cluster with pre-existing information it has to have
the same structure as specified in the documentation.

<a id="DatabaseManagement.BBDB.close"></a>

#### close

```python
def close()
```

Close the connection with the database

<a id="DatabaseManagement.BBDB.closeGraceful"></a>

#### closeGraceful

```python
def closeGraceful()
```

not needed for mongodb

<a id="DatabaseManagement.BBDB.commit"></a>

#### commit

```python
def commit()
```

not needed for mongodb

<a id="DatabaseManagement.BBDB.delUser"></a>

#### delUser

```python
def delUser(user_id: uuid.UUID) -> bool
```

Delete a user from the database.

**Arguments**:

- `user_id` - ID of the user that you want to delete.
  

**Returns**:

  Returns True if the user has been deleted and False otherwise.

<a id="DatabaseManagement.BBDB.addAdminRelation"></a>

#### addAdminRelation

```python
def addAdminRelation(user_id: uuid.UUID)
```

Add a user as an admin.

**Arguments**:

- `user_id` - ID of the user you want to add to add as admin
  

**Returns**:

  Returns True if the user has been added and False otherwise.

<a id="DatabaseManagement.BBDB.checkUserIDExists"></a>

#### checkUserIDExists

```python
def checkUserIDExists(uuid: typing.Optional[uuid.UUID])
```

Checks whether a certain uuid already exists.

**Arguments**:

- `uuid` - The user id that you want to verify.
  

**Returns**:

  Returns True if the user id exists already and false if it doesn't
  exist.

<a id="DatabaseManagement.BBDB.getUsername"></a>

#### getUsername

```python
def getUsername(uuids: list)
```

Fetches usernames from database belonging to the given uuids

**Arguments**:

- `uuids` - This is a list of user_uuid. Those are the uuids of which you want to get the usernames.
  

**Returns**:

  Returns the a list of usernames that correspond to the user_uuid
  that have been inputted. The index i of the return list corresponds
  to uuids[i] in the input. It a uuid doesn't belong to any user then None
  is returned for the entry.

<a id="DatabaseManagement.BBDB.login_user"></a>

#### login\_user

```python
def login_user(user_id: uuid.UUID)
```

Creates a new entry in the login_table for the user with the given uuid or username.

**Arguments**:

- `user_id` - ID of the user that you are login in.
  

**Returns**:

  Returns (False, False) if the login fails and the timestamp of the
  login if it succeeds.

<a id="DatabaseManagement.BBDB.update_login"></a>

#### update\_login

```python
def update_login(**kwargs)
```

Updates the status of the login of one user with the given user_uuid

Keyword arguments:
user_uuid -- ID of the user of which you want to log in.
time -- The timestamp of the login you want to update.
inserted_pic_uuid -- the uuid for the res in the resource table

**Returns**:

  Returns (False, False) if the access to the database hasn't been
  successful and returns the UUID (insert_pic_uuid) if the program
  has been successful.

<a id="DatabaseManagement.BBDB.getLoginLogOfUser"></a>

#### getLoginLogOfUser

```python
def getLoginLogOfUser(user_uuid: uuid.UUID)
```

Outputs log data of the user.

**Arguments**:

- `user_uuid` - The id of the user from which you want to get the log
  data.
  

**Returns**:

  A list containing multiple Lists with the following structure:
  [<login_date>, <res_id of success resource>]. If the a login at
  a certain date wasn't successful then the res_id will be None.

<a id="DatabaseManagement.BBDB.register_user"></a>

#### register\_user

```python
def register_user(username: str, user_enc: np.ndarray)
```

Creates a new user in the database with the given username.

**Arguments**:

- `username` - The username of the new user.
- `user_enc` - encoding of the user.
  

**Returns**:

  If the user has been successfully registered then it returns the
  user_id of the user what has been created.
  
  Exception:
  Raises an exception if the username already exists.

<a id="DatabaseManagement.BBDB.update_user_enc"></a>

#### update\_user\_enc

```python
def update_user_enc(user_uuid: uuid.UUID, user_enc: np.ndarray)
```

Updates the user encoding of a user.

**Arguments**:

- `user_uuid` - id of the user.
- `user_enc` - The user encoding to update.
  

**Returns**:

  Returns True if the encoding has been update and False otherwise.
  
  Exception:
  Raises a TypeError if the inputted encoding isn't a numpy array and
  raises a UserDoesntExist exception if the uuid doesn't belong to an
  existing user.

<a id="DatabaseManagement.BBDB.get_user_enc"></a>

#### get\_user\_enc

```python
def get_user_enc(user_uuid: uuid.UUID) -> np.ndarray
```

Get the user encoding from a certain user.

**Arguments**:

- `user_uuid` - The ID of the user.
  

**Returns**:

  Returns user encoding.
  
  Exception:
  Raises UserDoesntExist exception if the user doesn't exist.

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
  list with `limit` amount of entries. The dictionary key are the user_uuid
  (with type uuid.UUID) and the value is the username (with type str).

<a id="DatabaseManagement.BBDB.getUserWithId"></a>

#### getUserWithId

```python
def getUserWithId(user_id: uuid.UUID) -> typing.Optional[str]
```

Returns the username corresponding to the user_id.

**Arguments**:

- `user_id` - The user_id aka _id.
  

**Returns**:

  Returns the username corresponding to the user_id. If the user with the
  given ID doesn't exist then None gets returned.

<a id="DatabaseManagement.BBDB.deleteUserWithId"></a>

#### deleteUserWithId

```python
def deleteUserWithId(user_id: uuid.UUID) -> bool
```

Deletes the user with the given user_uuid from the database and all data cooresponding to it.

**Arguments**:

- `user_id` - ID of the user that should be deleted.
  

**Returns**:

  Returns True if the user has been successfully deleted. And
  False otherwise (e.g. user didn't exist in the database).

<a id="DatabaseManagement.BBDB.getUser"></a>

#### getUser

```python
def getUser(username: str) -> typing.Optional[uuid.UUID]
```

Returns the uuid corresponding to the username.

**Arguments**:

- `username` - The username of the user.
  

**Returns**:

  Returns the uuid corresponding to the username. If the username
  doesn't exist then it returns None.

<a id="DatabaseManagement.BBDB.getAllTrainingsImages"></a>

#### getAllTrainingsImages

```python
def getAllTrainingsImages()
```

This function has not been implemented.

Returns all training images from the database in three lists: 
pics, uuids, user_uuids

<a id="DatabaseManagement.BBDB.insertPicture"></a>

#### insertPicture

```python
def insertPicture(pic: np.ndarray, user_uuid: uuid.UUID)
```

This function has not been implemented.

<a id="DatabaseManagement.BBDB.getPicture"></a>

#### getPicture

```python
def getPicture(query: str)
```

This function has not been implemented.

<a id="DatabaseManagement.wire_DB"></a>

## wire\_DB Objects

```python
class wire_DB(BBDB)
```

<a id="DatabaseManagement.wire_DB.__init__"></a>

#### \_\_init\_\_

```python
def __init__(mongo_client=None)
```

<a id="DatabaseManagement.wire_DB.getTrainingPictures"></a>

#### getTrainingPictures

```python
def getTrainingPictures(user_uuid: typing.Optional[uuid.UUID] = None)
```

Returns training pictures from the database from the wire resource context

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

<a id="DatabaseManagement.wire_DB.insertPicture"></a>

#### insertPicture

```python
def insertPicture(pic: np.ndarray, user_uuid: uuid.UUID)
```

This function has not been implemented.

<a id="DatabaseManagement.wire_DB.getPicture"></a>

#### getPicture

```python
def getPicture(query: str)
```

This function has not been implemented.

<a id="DatabaseManagement.vid_DB"></a>

## vid\_DB Objects

```python
class vid_DB(BBDB)
```

Subclass from BBDB
Inherits Methods and Variables

<a id="DatabaseManagement.vid_DB.__init__"></a>

#### \_\_init\_\_

```python
def __init__(dbhost=None)
```

<a id="DatabaseManagement.vid_DB.insertVideo"></a>

#### insertVideo

```python
def insertVideo(vid, user_uuid: uuid.UUID, filename: str,
                video_transcript: str)
```

Inserts a new video into the database and returns the
uuid of the inserted video.

**Arguments**:

- `vid` - The source stream of the video that is getting uploaded.
  This has to be a file-like object that implements `read()`.
  Alternatively it's also allowed to be a string.
- `user_uuid` - ID of the user that owns the video.
- `filename` - Filename of the inserted data. The filename doesn't have to left empty
- `video_transcript` - The transcript of the video.
  

**Returns**:

  Returns the uuid of the video that has been inserted into the database.
  
  Exception:
- `TypeError` - Gets risen if the type of the input isn't the expected type.

<a id="DatabaseManagement.vid_DB.getVideoStream"></a>

#### getVideoStream

```python
def getVideoStream(vid_uuid: uuid.UUID, stream)
```

Writes video with certain id into the stream.

**Arguments**:

- `vid_uuid` - This is the id of the video that you want to get.
- `stream` - The destination stream of the video that is getting downloaded.
  This has to be a file-like object that implements `write()`.
  

**Returns**:

  Returns a list with [user_uuid, filename, video_transcript].
  
  Exception:
- `TypeError` - Gets risen if the type of the input isn't the expected type.
- `FileNotFoundError` - If the video with the id doesn't exist.

<a id="DatabaseManagement.vid_DB.getVideoIDOfUser"></a>

#### getVideoIDOfUser

```python
def getVideoIDOfUser(user_uuid: uuid.UUID) -> typing.List[uuid.UUID]
```

Outputs list of video ids from videos that belong to a certain user.

**Arguments**:

- `user_uuid` - This is the ID of the user from which you want to have the
  IDs of the video that belong to the user.
  

**Returns**:

  Returns a list of video IDs.
  
  Exception:
- `TypeError` - Gets risen if the type of the input isn't the expected type.

<a id="DatabaseManagement.vid_DB.deleteVideo"></a>

#### deleteVideo

```python
def deleteVideo(vid_uuid: uuid.UUID) -> bool
```

Deletes a video.

**Arguments**:

- `vid_uuid` - ID of the video that you want to delete.
  

**Returns**:

  Returns True if the video has been deleted and false otherwise.
  
  Exception:
- `TypeError` - Gets risen if the type of the input isn't the expected type.
- `gridfs.errors.NoFile` - Gets risen if the video doesn't exist.

<a id="DatabaseManagement.opencv_DB"></a>

## opencv\_DB Objects

```python
class opencv_DB(BBDB)
```

<a id="DatabaseManagement.opencv_DB.__init__"></a>

#### \_\_init\_\_

```python
def __init__()
```

<a id="DatabaseManagement.frontend_DB"></a>

## frontend\_DB Objects

```python
class frontend_DB(BBDB)
```

<a id="DatabaseManagement.frontend_DB.__init__"></a>

#### \_\_init\_\_

```python
def __init__()
```

<a id="DatabaseManagement.UsernameExists"></a>

## UsernameExists Objects

```python
class UsernameExists(Exception)
```

