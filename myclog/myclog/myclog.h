#ifndef __MYCLOG__
#define __MYCLOG__

#include <stdio.h>
#include <stdarg.h>
#include <time.h>
#include <string>
#include <assert.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>
#include <stdlib.h>

#ifdef _WIN32
#include <io.h>
#include <process.h>
#define sleep	Sleep
#define strcasecmp strcmpi
#define vsnprintf _vsnprintf
#define snprintf  _snprintf
#define F_OK  00	//Existence only
#define W_OK  02	//Write - only
#define R_OK  04	//Read - only
#define RW_OK  06	//Read and write
#define PATH_MAX			512
#else
#include <memory.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/time.h>
#include <limits.h>
#endif

using namespace std;

enum LOG_LEVEL
{
	log_trace = 0,
	log_debug = 10,
	log_info = 20,
	log_warn = 30,
	log_error = 40,
	log_critical = 50,
	log_close = 60
};


#define MAX_LOG_LINE		100000		// 单个日志文件最大记录行数
#define LOG_DIR_MODE        0755
#define ONE_DAY_SECONDS     86400

//-----------------------------------------------------------------------------
class MyCLog
{
public:
	MyCLog();
	virtual ~MyCLog();
public:

	int setLogHeader(const char *nm);	// 设置日志头名称

	int _canAccessDir(const char *dir);
	int setLogDir(const char *dir);

	int setLogLevel(const char* file_level = "trace", const char* term_level = "close");
	int setLogMaxLine(unsigned int limit = MAX_LOG_LINE);
	int setLogBufferSize(unsigned int size);

	int _logOpen();
	int flush();
	int close();

	int log(int level, const char *format, ...); //写日志
	int logWithoutFormat(int level, const char *msg); //写日志
	int println(int level, const char *format, ...); //写终端
	int get_fileno();
	
	inline bool isHigherFileLevel(int level)
	{
		//printf("level:%d, m_file_level:%d\n", level, m_file_level);
		return level >= m_file_level;
	}
	inline bool isHigherPrintLevel(int level)
	{
		return level >= m_print_level;
	}

protected:
	int m_file_level;
	int m_print_level;
	bool m_bNewLine;
	bool m_bNewDaySwitch;

	unsigned int m_log_max_line; // 单日志文件最大行数, 大了则自动切换文件
	unsigned int m_log_line_pos;
	unsigned int m_log_name_index; // log文件名后缀 1, 2, 3

	char m_filepath[PATH_MAX];
	char m_prefix[64];
	char m_logdir[PATH_MAX];

	FILE *m_log_fd;
	char *m_szBuf;
	int m_nBufferSize;
	struct tm m_date;
};

#define R5_LOG(plog, level, X) \
    do{\
      if ( plog->isHigherFileLevel( level ) )\
      {\
        plog->log X;\
      }\
      if ( plog->isHigherPrintLevel( level ) )\
      {\
        plog->print X;\
      }\
    }while(0)

#define R5_INFO(plog, X) \
      R5_LOG((plog),r5_log_info, X);

#define R5_WARN(plog, X) \
      R5_LOG((plog), r5_log_warn, X);

#define R5_ERROR(plog, X) \
       R5_LOG((plog), r5_log_error, X);

#define R5_FATAL(plog, X) \
      R5_LOG((plog), r5_log_fatal, X);

#define R5_END(plog, X) \
       R5_LOG((plog), r5_log_end, X);

#ifdef NR5_LOG
#define TRACE(plog, X) do{} while(0)
#define DEBUG(plog, X) do{} while(0)
#else

#define R5_TRACE(plog, X) \
      R5_LOG((plog), r5_log_trace, X);

#define R5_DEBUG(plog, X) \
      R5_LOG((plog), r5_log_debug, X);
#endif

#endif //__MYCLOG__

