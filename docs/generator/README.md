# API Documentation
This is the documentation of the API. You can find the functions and modules
that have been implemented in there:
- [DatabaseManagement](databasemanagement.md)
## Maintainance/Generation
In order to generate the API Documentation we use
[pydoc-markdown](https://pypi.org/project/pydoc-markdown/). In order to compile
go to the [generator](../generator)-directory and call:
```
pydoc-markdown
```
in the command window. If you add files or functions make sure that they 
are also visible in the API Documentation after using `pydoc-markdown`. 
If not you might modify the [pydoc-markdown.yml](../generator/pydoc-markdown.yml)-file:
- Perhaps you need to add a new path in `search\_path` or
- Add a new `title`, `name` or `contents` in the `pages`-section to make
it work.

