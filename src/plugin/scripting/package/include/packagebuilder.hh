/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/plugin.scripting.package/nodes/package.hh>

namespace Motor { namespace PackageBuilder {

class PackageBuilder : public minitl::pointer
{
private:
    ref< Folder > m_dataFolder;

public:
    explicit PackageBuilder(const ref< Folder >& dataFolder);
    ~PackageBuilder() override;

public:
    ref< Nodes::Package > createPackage(const ifilename&                      filename,
                                        const minitl::Allocator::Block< u8 >& buffer);
};

}}  // namespace Motor::PackageBuilder
