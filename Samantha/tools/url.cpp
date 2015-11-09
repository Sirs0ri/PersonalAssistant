#include <CkHttp.h>
#include <CkString.h>

CkHttp http;
CkString html;
html = http.quickGetStr("http://www.w3.org/Protocols/");

printf("%s\n",(const char *)html);