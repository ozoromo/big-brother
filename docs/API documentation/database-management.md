<a id="base_database"></a>

# base\_database

<a id="base_database.BaseDatabase"></a>

## BaseDatabase Objects

```python
class BaseDatabase()
```

Database Baseclass

<a id="base_database.BaseDatabase.__init__"></a>

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

<a id="base_database.BaseDatabase.close"></a>

#### close

```python
def close()
```

Close the connection with the database

<a id="base_database.BaseDatabase.delete_user"></a>

#### delete\_user

```python
def delete_user(user_id: uuid.UUID) -> bool
```

Delete a user from the database.

**Arguments**:

- `user_id` - ID of the user that you want to delete.
  

**Returns**:

  Returns True if the user has been deleted and False otherwise.

<a id="base_database.BaseDatabase.add_admin_relation"></a>

#### add\_admin\_relation

```python
def add_admin_relation(user_id: uuid.UUID)
```

Add a user as an admin.

**Arguments**:

- `user_id` - ID of the user you want to add to add as admin
  

**Returns**:

  Returns True if the user has been added and False otherwise.

<a id="base_database.BaseDatabase.check_user_id_exists"></a>

#### check\_user\_id\_exists

```python
def check_user_id_exists(uuid: typing.Optional[uuid.UUID])
```

Checks whether a certain uuid already exists.

**Arguments**:

- `uuid` - The user id that you want to verify.
  

**Returns**:

  Returns True if the user id exists already and false if it doesn't
  exist.

<a id="base_database.BaseDatabase.get_username"></a>

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
  to uuids[i] in the input. It a uuid doesn't belong to any user then None
  is returned for the entry.

<a id="base_database.BaseDatabase.login_user"></a>

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

<a id="base_database.BaseDatabase.update_login"></a>

#### update\_login

```python
def update_login(user_uuid: uuid.UUID, time: dt.datetime,
                 success_res_uuid: typing.Optional[uuid.UUID])
```

Updates the status of the login of one user with the given user_uuid

**Arguments**:

- `user_uuid` - ID of the user of which you want to log in.
- `time` - The timestamp of the login you want to update.
- `success_red_uuid` - the uuid for the res in the resource table.
  

**Returns**:

  Returns False if the access to the database hasn't been
  successful and returns the UUID (insert_pic_uuid) if the program
  has been successful.
  
  Exception:
- `ValueError` - Raised if the types of the input is not correct.

<a id="base_database.BaseDatabase.get_login_log_of_user"></a>

#### get\_login\_log\_of\_user

```python
def get_login_log_of_user(user_uuid: uuid.UUID)
```

Outputs log data of the user.

**Arguments**:

- `user_uuid` - The id of the user from which you want to get the log
  data.
  

**Returns**:

  A list containing multiple Lists with the following structure:
  [<login_date>, <res_id of success resource>]. If the a login at
  a certain date wasn't successful then the res_id will be None.

<a id="base_database.BaseDatabase.register_user"></a>

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

<a id="base_database.BaseDatabase.update_user_enc"></a>

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
  raises a UserDoesntExistException exception if the uuid doesn't belong to an
  existing user.

<a id="base_database.BaseDatabase.get_user_enc"></a>

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
  Raises UserDoesntExistException exception if the user doesn't exist.

<a id="base_database.BaseDatabase.get_users"></a>

#### get\_users

```python
def get_users(limit=-1)
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

<a id="base_database.BaseDatabase.get_user_with_id"></a>

#### get\_user\_with\_id

```python
def get_user_with_id(user_id: uuid.UUID) -> typing.Optional[str]
```

Returns the username corresponding to the user_id.

**Arguments**:

- `user_id` - The user_id aka _id.
  

**Returns**:

  Returns the username corresponding to the user_id. If the user with the
  given ID doesn't exist then None gets returned.

<a id="base_database.BaseDatabase.delete_user_with_id"></a>

#### delete\_user\_with\_id

```python
def delete_user_with_id(user_id: uuid.UUID) -> bool
```

Deletes the user with the given user_uuid from the database and all data cooresponding to it.

**Arguments**:

- `user_id` - ID of the user that should be deleted.
  

**Returns**:

  Returns True if the user has been successfully deleted. And
  False otherwise (e.g. user didn't exist in the database).

<a id="base_database.BaseDatabase.get_user"></a>

#### get\_user

```python
def get_user(username: str) -> typing.Optional[uuid.UUID]
```

Returns the uuid corresponding to the username.

**Arguments**:

- `username` - The username of the user.
  

**Returns**:

  Returns the uuid corresponding to the username. If the username
  doesn't exist then it returns None.

<a id="picture_database"></a>

# picture\_database

<a id="picture_database.PictureDatabase"></a>

## PictureDatabase Objects

```python
class PictureDatabase(BaseDatabase)
```

This database stores pictures. This is specifically made in order to manage
storing and getting pictures from the database.

<a id="picture_database.PictureDatabase.__init__"></a>

#### \_\_init\_\_

```python
def __init__(mongo_client=None)
```

<a id="picture_database.PictureDatabase.get_pictures"></a>

#### get\_pictures

```python
def get_pictures(user_uuid: typing.Optional[uuid.UUID] = None)
```

Returns training pictures from the database from the wire resource context

<a id="picture_database.PictureDatabase.insert_picture"></a>

#### insert\_picture

```python
def insert_picture(pic: np.ndarray, user_uuid: uuid.UUID)
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

<a id="video_database"></a>

# video\_database

<a id="video_database.VideoDatabase"></a>

## VideoDatabase Objects

```python
class VideoDatabase(BaseDatabase)
```

This database stores videos. This is specifically made in order to manage
storing and getting videos from the database.

<a id="video_database.VideoDatabase.__init__"></a>

#### \_\_init\_\_

```python
def __init__(dbhost=None)
```

<a id="video_database.VideoDatabase.insert_video"></a>

#### insert\_video

```python
def insert_video(vid, user_uuid: uuid.UUID, filename: str,
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
- `UserDoesntExistException` - Gets risen if the user doesn't exist.

<a id="video_database.VideoDatabase.get_video_stream"></a>

#### get\_video\_stream

```python
def get_video_stream(vid_uuid: uuid.UUID, stream)
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

<a id="video_database.VideoDatabase.get_video_id_of_user"></a>

#### get\_video\_id\_of\_user

```python
def get_video_id_of_user(user_uuid: uuid.UUID) -> typing.List[uuid.UUID]
```

Outputs list of video ids from videos that belong to a certain user.

**Arguments**:

- `user_uuid` - This is the ID of the user from which you want to have the
  IDs of the video that belong to the user.
  

**Returns**:

  Returns a list of video IDs.
  
  Exception:
- `TypeError` - Gets risen if the type of the input isn't the expected type.

<a id="video_database.VideoDatabase.delete_video"></a>

#### delete\_video

```python
def delete_video(vid_uuid: uuid.UUID) -> bool
```

Deletes a video.

**Arguments**:

- `vid_uuid` - ID of the video that you want to delete.
  

**Returns**:

  Returns True if the video has been deleted and false otherwise.
  
  Exception:
- `TypeError` - Gets risen if the type of the input isn't the expected type.
- `gridfs.errors.NoFile` - Gets risen if the video doesn't exist.

