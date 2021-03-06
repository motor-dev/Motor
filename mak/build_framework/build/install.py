from waflib import Errors, Logs, Task, Utils
from waflib.TaskGen import feature, before_method, after_method
import os
import shutil


class install(Task.Task):
    color = 'CYAN'

    def runnable_status(self):
        ret = super(install, self).runnable_status()
        if ret != Task.ASK_LATER:
            for source, target, chmod in self.install_step:
                d, _ = os.path.split(target)
                if not d:
                    raise Errors.WafError('Invalid installation given %r->%r' % (source, target))

                try:
                    st1 = os.stat(target)
                    st2 = os.stat(source.abspath())
                except OSError:
                    ret = Task.RUN_ME
                    break
                else:
                    # same size and identical timestamps -> make no copy
                    if st1.st_mtime + 2 < st2.st_mtime or st1.st_size != st2.st_size:
                        ret = Task.RUN_ME
                        break
        return ret

    def run(self):
        for source, target, chmod in self.install_step:
            d, _ = os.path.split(target)
            Utils.check_dir(d)
            # following is for shared libs and stale inodes (-_-)
            try:
                os.remove(target)
            except OSError:
                pass

            try:
                shutil.copy2(source.abspath(), target)
                os.chmod(target, chmod)
            except IOError:
                try:
                    os.stat(source.abspath())
                except (OSError, IOError):
                    Logs.error('File %r does not exist' % source.abspath())
                    return 1
                Logs.error('Could not install the file %r' % target)
                return 1
        return 0


@feature('motor:deploy:off')
def dummy_deploy_off(self):
    pass


@feature('motor:preprocess')
def install_module_files(self):
    if 'motor:deploy:off' not in self.features:
        env = self.env
        for source_node in self.source_nodes:
            bin_paths = [
                i for i in [source_node.make_node('bin')] +
                [source_node.make_node('bin.%s' % p) for p in env.VALID_PLATFORMS] if os.path.isdir(i.abspath())
            ]
            data_paths = [
                i for i in [source_node.make_node('data')] +
                [source_node.make_node('data.%s' % p) for p in env.VALID_PLATFORMS] if os.path.isdir(i.abspath())
            ]
            for bin_path in bin_paths:
                self.install_directory(env, bin_path, '', 'DEPLOY_RUNBINDIR')
            for data_path in data_paths:
                self.install_directory(env, data_path, '', 'DEPLOY_DATADIR')


@feature('motor:kernel')
@after_method('install_step')
def install_kernel(self):
    if not self.env.SUBARCH and not self.bld.env.STATIC:                                          #no multiarch, no static
        self.install_files(
            os.path.join(self.bld.env.PREFIX, self.bld.optim, self.bld.env.DEPLOY_KERNELDIR),
            [self.postlink_task.outputs[0]], Utils.O755
        )
        if self.env.CC_NAME == 'msvc':
            self.install_files(
                os.path.join(self.bld.env.PREFIX, self.bld.optim, self.bld.env.DEPLOY_KERNELDIR),
                [self.link_task.outputs[1]]
            )


@feature('motor:plugin')
@after_method('install_step')
def install_plugin(self):
    if ('cshlib' in self.features) or ('cxxshlib' in self.features):
        if not self.env.SUBARCH:                                                                      #no multiarch
            self.install_files(
                os.path.join(self.bld.env.PREFIX, self.bld.optim, self.bld.env.DEPLOY_PLUGINDIR),
                [self.postlink_task.outputs[0]], Utils.O755
            )
            if self.env.CC_NAME == 'msvc':
                self.install_files(
                    os.path.join(self.bld.env.PREFIX, self.bld.optim, self.bld.env.DEPLOY_PLUGINDIR),
                    [self.link_task.outputs[1]]
                )


@feature('motor:shared_lib')
@after_method('install_step')
def install_shared_lib(self):
    if ('cshlib' in self.features) or ('cxxshlib' in self.features):
        if not self.env.SUBARCH:                                                                      #no multiarch
            self.install_files(
                os.path.join(self.bld.env.PREFIX, self.bld.optim, self.bld.env.DEPLOY_RUNBINDIR),
                [self.postlink_task.outputs[0]], Utils.O755
            )
            if self.env.CC_NAME == 'msvc':
                self.install_files(
                    os.path.join(self.bld.env.PREFIX, self.bld.optim, self.bld.env.DEPLOY_RUNBINDIR),
                    [self.link_task.outputs[1]]
                )


@feature('motor:launcher')
@after_method('install_step')
def install_program(self):
    if not self.env.SUBARCH:                                                                   #no multiarch
        self.install_files(
            os.path.join(self.bld.env.PREFIX, self.bld.optim, self.bld.env.DEPLOY_BINDIR),
            [self.postlink_task.outputs[0]],
            chmod=Utils.O755
        )
        if self.env.CC_NAME == 'msvc':
            self.install_files(
                os.path.join(self.bld.env.PREFIX, self.bld.optim, self.bld.env.DEPLOY_BINDIR),
                [self.link_task.outputs[1]]
            )


@feature('motor:game')
@after_method('install_step')
def install_game(self):
    pass   #also plugin


def build(bld):
    pass
