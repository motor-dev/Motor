---@meta

local function use(var)
    return var
end

---Registers a feature callback.
---@param feature string|string[] A list of features that this callback is attached to.
---@param name string The name of this step.
---@param callback function(generator: Generator) The function attached to the feature.
---@return Feature A new feature object that can be used to set predecence
function Context:feature(feature, name, callback)
    use(feature)
    use(name)
    use(callback)
    use(after)
    use(before)
    return Feature
end

---Posts a generator. Calls all methods associated with the features, which can in turn post other generators or create tasks.
---@param generator Generator the generator to post. Posting the generator more than once has no effect.
function Context:post(generator)
    use(generator)
end

---@class Feature
Feature = {}

---Adds a list of steps that are prerequisites for this step. The function returns an error if setting the dependencies
---would create a dependency cycle. In this case, no dependency is added.
---@param predecessors string[] An optional list of steps that this step comes after, i.e. must have been executed before this step.
---@return Feature the same object for further editing
function Feature:set_run_after(predecessors)
    use(predecessors)
    return self
end

---Adds a list of steps that the current step is a prerequisite of. The function returns an error if setting the dependencies
---would create a dependency cycle. In this case, no dependency is added.
---@param successors string[] An optional list of steps that this step comes before, i.e. must be executed after this step.
---@return Feature the same object for further editing
function Feature:set_run_before(successors)
    use(successors)
    return self
end
