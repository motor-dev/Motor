--- @type Context
context = ...

if context.name == "init" then
    context:declare_command("do", "do")
else
    context:declare_generator("test_stage1", "stage1")

    context:feature("stage1", "stage1", function()
        context:declare_generator("test_stage2", "stage2")
    end)
    context:feature("stage2", "stage2", function()
        context:declare_generator("test_stage3", "stage3")
    end)

    context:feature("stage3", "stage3", function()
        print("stage3")
    end)
end
