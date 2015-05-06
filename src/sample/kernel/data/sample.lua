kernel = plugin("sample.kernel")
_3d = plugin("plugin.graphics.3d")

tokens={}

storage = kernel.KernelStorage()
sample = kernel.Kernels.Add(
    getattr(storage, "A+B").A,
    getattr(storage, "A+B").B,
    getattr(storage, "A+C").C,
    getattr(storage, "A+D+E").D,
    getattr(storage, "A+D+E").E)
tokens['sample'] = resources:load(sample)
world = BugEngine.World.World(storage, {sample.output})
tokens['world'] = resources:load(world)

e0 = world:spawn()
e1 = world:spawn()
e2 = world:spawn()
e3 = world:spawn()
e4 = world:spawn()
e5 = world:spawn()
e6 = world:spawn()
e7 = world:spawn()
e8 = world:spawn()
e9 = world:spawn()
e10 = world:spawn()
e11 = world:spawn()
e12 = world:spawn()
e13 = world:spawn()
e14 = world:spawn()
e15 = world:spawn()
e16 = world:spawn()
e17 = world:spawn()
e18 = world:spawn()

world:addComponent(e0, kernel.A({value = 100}))
world:addComponent(e1, kernel.A({value = 101}))
world:addComponent(e1, kernel.B({value = 201}))
world:addComponent(e2, kernel.A({value = 102}))
world:addComponent(e2, kernel.B({value = 202}))
world:addComponent(e2, kernel.C({value = 302}))
world:addComponent(e3, kernel.A({value = 103}))
world:addComponent(e3, kernel.B({value = 203}))
world:addComponent(e3, kernel.C({value = 303}))
world:addComponent(e3, kernel.D({value = 403}))
world:addComponent(e4, kernel.A({value = 104}))
world:addComponent(e4, kernel.C({value = 304}))
world:addComponent(e5, kernel.A({value = 105}))
world:addComponent(e5, kernel.C({value = 305}))
world:addComponent(e5, kernel.D({value = 405}))
world:addComponent(e6, kernel.A({value = 106}))
world:addComponent(e6, kernel.D({value = 406}))
world:addComponent(e7, kernel.A({value = 107}))
world:addComponent(e7, kernel.C({value = 307}))
world:addComponent(e7, kernel.D({value = 407}))
world:addComponent(e8, kernel.B({value = 208}))
world:addComponent(e9, kernel.B({value = 209}))
world:addComponent(e9, kernel.C({value = 309}))
world:addComponent(e10, kernel.B({value = 210}))
world:addComponent(e10, kernel.C({value = 310}))
world:addComponent(e10, kernel.D({value = 410}))
world:addComponent(e11, kernel.C({value = 311}))
world:addComponent(e12, kernel.C({value = 312}))
world:addComponent(e12, kernel.D({value = 412}))
world:addComponent(e13, kernel.D({value = 413}))
world:addComponent(e14, kernel.C({value = 314}))
world:addComponent(e14, kernel.A({value = 114}))
world:addComponent(e14, kernel.D({value = 414}))
world:addComponent(e14, kernel.E({value = 514}))
world:addComponent(e15, kernel.A({value = 115}))
world:addComponent(e15, kernel.D({value = 415}))
world:addComponent(e15, kernel.E({value = 515}))
world:addComponent(e16, kernel.A({value = 116}))
world:addComponent(e16, kernel.B({value = 216}))
world:addComponent(e16, kernel.D({value = 416}))
world:addComponent(e16, kernel.E({value = 516}))
world:addComponent(e17, kernel.A({value = 117}))
world:addComponent(e17, kernel.B({value = 217}))
world:addComponent(e17, kernel.C({value = 317}))
world:addComponent(e17, kernel.D({value = 417}))
world:addComponent(e17, kernel.E({value = 517}))
storage:start()
world:removeComponent(e0, kernel.A)
world:removeComponent(e1, kernel.A)
world:removeComponent(e2, kernel.A)
storage:start()
