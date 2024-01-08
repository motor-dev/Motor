import waflib.Task
from typing import Callable, Tuple, Type, TypeVar

T = TypeVar('T', bound=waflib.Task.Task)


def autosig_vars(*variables: str) -> Callable[[Type[T]], Type[T]]:
    def autosig(task_class: Type[T]) -> Type[T]:
        sig_vars = getattr(task_class, 'sig_vars')  # type: Callable[[T], None]

        def auto_sig_vars(task: T) -> None:
            sig_vars(task)
            for var in variables:
                task.m.update(str(getattr(task, var)).encode())

        setattr(task_class, 'sig_vars', auto_sig_vars)
        return task_class

    return autosig


def autosig_env(*variables: str) -> Callable[[Type[T]], Type[T]]:
    def autosig(task_class: Type[T]) -> Type[T]:
        sig_vars = getattr(task_class, 'sig_vars')  # type: Callable[[T], None]

        def auto_sig_vars(task: T) -> None:
            sig_vars(task)
            for env_var in variables:
                task.m.update(str(task.env[env_var]).encode())

        setattr(task_class, 'sig_vars', auto_sig_vars)
        return task_class

    return autosig


def autosig_generator(*variables: str) -> Callable[[Type[T]], Type[T]]:
    def autosig(task_class: Type[T]) -> Type[T]:
        sig_vars = getattr(task_class, 'sig_vars')  # type: Callable[[T], None]

        def auto_sig_vars(task: T) -> None:
            sig_vars(task)
            for var in variables:
                task.m.update(str(getattr(task.generator, var)).encode())

        setattr(task_class, 'sig_vars', auto_sig_vars)
        return task_class

    return autosig
