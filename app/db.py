from sqlobject import (
    sqlhub,
    connectionForURI,
    SQLObject,
    StringCol,
    IntCol,
    DateTimeCol,
    ForeignKey,
    sqlbuilder,
)
import os

db_filename = os.path.abspath("data.db")
connection_string = f"sqlite:{db_filename}"
sqlhub.processConnection = connectionForURI(connection_string)


class Users(SQLObject):
    uid = StringCol()
    username = StringCol()
    password = StringCol()
    createPasswordMode = IntCol()
    email = StringCol()
    classLevel = IntCol()

    def toDict(self):
        return {
            "id": self.id,
            "uid": self.uid,
            "username": self.username,
            "password": self.password,
            "createPasswordMode": self.createPasswordMode,
            "email": self.email,
            "classLevel": self.classLevel,
        }


class BackgroundsList(SQLObject):
    image = StringCol()

    def toDict(self):
        return {
            "id": self.id,
            "image": self.image,
        }


class GlobalSettings(SQLObject):
    selectedImage = IntCol()

    def toDict(self):
        return {
            "selectedImage": self.selectedImage,
        }


Users.createTable(ifNotExists=True)
BackgroundsList.createTable(ifNotExists=True)
GlobalSettings.createTable(ifNotExists=True)
