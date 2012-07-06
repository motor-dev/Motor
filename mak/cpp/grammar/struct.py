import cpp


class MemberList(cpp.yacc.Nonterm):
	"%nonterm"

	def empty(self):
		"%reduce"
		self.members = [None, None, None, None, None]

	def block(self, visibility, colon, exprs, memberlist):
		"%reduce Visibility COLON Exprs MemberList"
		self.members = memberlist.members
		if self.members[visibility.visibility]:
			self.members[visibility.visibility].members += exprs.members
			self.members[visibility.visibility].objects += exprs.objects
			for m, methods in exprs.methods.items():
				try:
					self.members[visibility.visibility].methods[m] += methods
				except KeyError:
					self.members[visibility.visibility].methods[m] = methods
		else:
			self.members[visibility.visibility] = exprs


class Members(cpp.yacc.Nonterm):
	"%nonterm"

	def list(self, exprs, members):
		"%reduce Exprs MemberList"
		self.members = members.members
		self.members[3] = exprs

class Visibility(cpp.yacc.Nonterm):
	"%nonterm"

	def private(self, private):
		"%reduce PRIVATE"
		self.visibility = 0
	def protected(self, protected):
		"%reduce PROTECTED"
		self.visibility = 1
	def none(self):
		"%reduce"
		self.visibility = 2
	def public(self, public):
		"%reduce PUBLIC"
		self.visibility = 3
	def published(self, published):
		"%reduce PUBLISHED"
		self.visibility = 4




class ParentList(cpp.yacc.Nonterm):
	"%nonterm"

	def parent_item(self, visibility, name):
		"%reduce Visibility Name"
		self.inherits = (visibility.visibility, name.value)
	def parent_list(self, parent_list, comma, visibility, name):
		"%reduce ParentList COMMA Visibility Name"
		if visibility.visibility > parent_list.inherits[0]:
			self.inherits = (visibility.visibility, name.value)
		else:
			self.inherits = parent_list.inherits




class Parent(cpp.yacc.Nonterm):
	"%nonterm"

	def parent_none(self):
		"%reduce"
		self.inherits = (0, "")
	def parent_list(self, colon, parent_list):
		"%reduce COLON ParentList"
		self.inherits = parent_list.inherits




class ClassDef(cpp.yacc.Nonterm):
	"%nonterm"

	def class_definition(self, cls, name, parent, lbrace, members, rbrace):
		"%reduce CLASS NameOpt Parent LBRACE Members RBRACE"
		self.name = name.value.replace(' ', '')
		self.decl = name.value.replace(' ', '').replace(':', '_').replace('<', '__').replace('>', '__')
		self.lineno = cls.lineno
		self.value = False
		self.pod = False
		self.members = members.members[4]
		if parent.inherits[0] >= 3:
			self.inherits = parent.inherits[1]
		else:
			self.inherits = "void"

	def struct_definition(self, cls, name, parent, lbrace, members, rbrace):
		"%reduce STRUCT NameOpt Parent LBRACE Members RBRACE"
		self.name = name.value.replace(' ', '')
		self.decl = name.value.replace(' ', '').replace(':', '_').replace('<', '__').replace('>', '__')
		self.lineno = cls.lineno
		self.value = True
		self.pod = False
		self.members = members.members[3]
		if self.members and members.members[4]:
			self.members.members += members.members[4].members
			self.members.objects += members.members[4].objects
			for m, methods in members.members[4].methods.items():
				try:
					self.members.methods[m] += methods
				except KeyError:
					self.members.methods[m] = methods
		else:
			self.members = members.members[4]
		if parent.inherits[0] >= 2:
			self.inherits = parent.inherits[1]
		else:
			self.inherits = "void"


	def pod_definition(self, cls, name, parent, lbrace, members, rbrace):
		"%reduce BE_POD NameOpt Parent LBRACE Members RBRACE"
		self.name = name.value.replace(' ', '')
		self.decl = name.value.replace(' ', '').replace(':', '_').replace('<', '__').replace('>', '__')
		self.lineno = cls.lineno
		self.value = True
		self.pod = True
		self.members = members.members[3]
		if self.members and members.members[4]:
			self.members.members += members.members[4].members
			self.members.objects += members.members[4].objects
			for m, methods in members.members[4].methods.items():
				try:
					self.members.methods[m] += methods
				except KeyError:
					self.members.methods[m] = methods
		else:
			self.members = members.members[4]
		if parent.inherits[0] >= 2:
			self.inherits = parent.inherits[1]
		else:
			self.inherits = "void"

	def union_definition(self, union, name, lbrace, members, rbrace):
		"%reduce UNION NameOpt LBRACE Members RBRACE"
		self.name = name.value.replace(' ', '')
		self.decl = name.value.replace(' ', '').replace(':', '_').replace('<', '__').replace('>', '__')
		self.lineno = union.lineno
		self.inherits = 'void'
		self.value = True
		self.pod = True
		self.members = members.members[4]

	def using(self, file, instances, decl, name, parent_name):
		pass

	def predecl(self, file, instances, decl, name, member):
		name = name+[self.name]
		decl = decl+[self.decl]
		fullname = '::'+'::'.join(name)
		prefix = "class%s" % '_'.join(decl)
		if self.parser.useMethods:
			instances.write("extern const ::BugEngine::RTTI::Class& s_%sFun();\n" % prefix)
			if self.pod:
				instances.write("extern const ::BugEngine::RTTI::Class& s_pod_def_%sFun();\n" % prefix)
		else:
			instances.write("extern ::BugEngine::RTTI::Class s_%s;\n" % (prefix))
			if self.pod:
				instances.write("extern ::BugEngine::RTTI::Class s_pod_def_%s;\n" % (prefix))
		if self.members:
			self.members.predecl(file, instances, decl, name, self.value)


	def create_pod_def(self, file, instances, name, prefix):
		file.write("#line %d\n"%self.lineno)
		if self.parser.useMethods:
			file.write("static ")
		file.write("::BugEngine::RTTI::Class s_pod_def_%s =\n" % (prefix))
		file.write("#line %d\n"%self.lineno)
		file.write("    {\n")
		file.write("#line %d\n"%self.lineno)
		file.write("        ::BugEngine::inamespace(\"BugEngine.Kernel.Stream<%s>\"),\n" % (self.name))
		file.write("#line %d\n"%self.lineno)
		file.write("        ::BugEngine::be_typeid< BugEngine::Kernel::IStream >::klass(),\n")
		file.write("#line %d\n"%self.lineno)
		file.write("        be_checked_numcast<u16>(sizeof(BugEngine::Kernel::Stream< %s >)),\n" % name)
		file.write("#line %d\n"%self.lineno)
		file.write("        be_checked_numcast<u16>(be_alignof(BugEngine::Kernel::Stream< %s >)),\n" % name)
		file.write("#line %d\n"%self.lineno)
		file.write("        be_checked_numcast<i32>((ptrdiff_t)static_cast< BugEngine::Kernel::IStream* >((BugEngine::Kernel::Stream< %s >*)1)-1),\n" % (name))
		file.write("#line %d\n"%self.lineno)
		file.write("        {0},\n")
		file.write("#line %d\n"%self.lineno)
		file.write("        {0},\n")
		file.write("#line %d\n"%self.lineno)
		file.write("        {0},\n")
		file.write("#line %d\n"%self.lineno)
		file.write("        {0},\n")
		file.write("#line %d\n"%self.lineno)
		file.write("        {0},\n")
		file.write("#line %d\n"%self.lineno)
		file.write("        {0},\n")
		file.write("#line %d\n"%self.lineno)
		file.write("        0,\n")
		file.write("#line %d\n"%self.lineno)
		file.write("        0\n")
		file.write("#line %d\n"%self.lineno)
		file.write("    };\n")
		instances.write("#line %d\n"%self.lineno)
		instances.write("template< > BE_EXPORT raw<const RTTI::Class> be_typeid< BugEngine::Kernel::Stream<%s> >::klass() { raw<const RTTI::Class> ci = {&s_pod_def_%s}; return ci; }\n" % (name, prefix))

	def dump(self, file, instances, namespace, decl, name, member):
		ns = '::'.join(namespace)
		name = name+[self.name]
		decl = decl+[self.decl]
		fullname = '::'.join(name)
		prettyname = '.'.join(name)
		prefix = "class%s" % '_'.join(decl)

		if self.pod:
			self.create_pod_def(file, instances, fullname,  prefix)
			

		if self.members:
			self.members.dumpObjects(file, instances, namespace, decl, name, fullname)

		if member:
			file.write("#line %d\n"%self.lineno)
			file.write("typedef %s %s;\n" % ('::'.join(name), self.name))

		if self.parser.useMethods:
			varname = "%s::s_%sFun()" % (ns, prefix)
			file.write("#line %d\n"%self.lineno)
			file.write("const ::BugEngine::RTTI::Class& s_%sFun ()\n{\n" % prefix)
		else:
			varname = "%s::s_%s" % (ns, prefix)

		tag_ptr = self.tags.dump(file, instances, prefix)
		if self.members:
			objects,methods,constructor,cast,properties = self.members.dump(file, instances, namespace, decl, name, fullname, self.inherits, self.value)
		else:
			objects = methods = constructor = cast = properties = "{0}"

		file.write("#line %d\n"%self.lineno)
		if self.parser.useMethods:
			file.write("static ")
		file.write("::BugEngine::RTTI::Class s_%s =\n" % (prefix))
		file.write("#line %d\n"%self.lineno)
		file.write("    {\n")
		file.write("#line %d\n"%self.lineno)
		file.write("        ::BugEngine::inamespace(\"%s\"),\n" % (prettyname))
		file.write("#line %d\n"%self.lineno)
		file.write("        ::BugEngine::be_typeid< %s >::klass(),\n" % (self.inherits))
		file.write("#line %d\n"%self.lineno)
		file.write("        be_checked_numcast<u16>(sizeof(%s)),\n" % fullname)
		file.write("#line %d\n"%self.lineno)
		file.write("        be_checked_numcast<u16>(be_alignof(%s)),\n" % fullname)
		file.write("#line %d\n"%self.lineno)
		file.write("        be_checked_numcast<i32>((ptrdiff_t)static_cast< %s* >((%s*)1)-1),\n" % (self.inherits, fullname))
		file.write("#line %d\n"%self.lineno)
		file.write("        %s,\n" % (tag_ptr))
		file.write("#line %d\n"%self.lineno)
		file.write("        %s,\n" % (properties))
		file.write("#line %d\n"%self.lineno)
		file.write("        %s,\n" % (methods))
		file.write("#line %d\n"%self.lineno)
		file.write("        %s,\n" % (objects))
		file.write("#line %d\n"%self.lineno)
		file.write("        %s,\n" % (constructor))
		file.write("#line %d\n"%self.lineno)
		file.write("        %s,\n" % (cast))
		if self.value:
			file.write("#line %d\n"%self.lineno)
			file.write("        &::BugEngine::RTTI::wrapCopy< %s >,\n" % fullname)
			file.write("#line %d\n"%self.lineno)
			file.write("        &::BugEngine::RTTI::wrapDestroy< %s >\n" % fullname)
		else:
			file.write("#line %d\n"%self.lineno)
			file.write("        0,\n")
			file.write("#line %d\n"%self.lineno)
			file.write("        0\n")
		file.write("#line %d\n"%self.lineno)
		file.write("    };\n")
		alias_index = 0
		if self.parser.useMethods:
			file.write("return s_%s;\n}\n" % prefix)

		instances.write("#line %d\n"%self.lineno)
		instances.write("template< > BE_EXPORT raw<const RTTI::Class> be_typeid< %s >::klass() { raw<const RTTI::Class> ci = {&%s}; return ci; }\n" % (fullname, varname))

		return varname, tag_ptr
