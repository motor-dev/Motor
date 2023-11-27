from ..Task import Task


class JTask(Task):
    ...


class jar_create(JTask):
    ...


class javac(JTask):

    def uid(self) -> bytes:
        ...


class javadoc(Task):
    ...
