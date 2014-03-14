/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#ifndef BE_TEXT_BITMAPFONT_SCRIPT_HH_
#define BE_TEXT_BITMAPFONT_SCRIPT_HH_
/**************************************************************************************************/
#include    <filesystem/file.script.hh>
#include    <resource/description.script.hh>

namespace BugEngine
{

class BitmapFontManager;

class be_api(TEXT) BitmapFont : public Resource::Description
{
    friend class BitmapFontManager;
private:
    istring const                       m_fontSystemName;
    weak<const File> const              m_fontFile;
published:
    BitmapFont(const istring& fontSystemName);
    BitmapFont(weak<const File> fontFile);
    ~BitmapFont();
};

}

/**************************************************************************************************/
#endif