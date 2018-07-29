
#include "myclog.h"

const char *LOG_LEVEL[] =
{
	"T",
	"D",
	"I",
	"W",
	"E",
	"F"
};

#ifdef _WIN32
#pragma warning(disable:4996)
#include <windows.h>
#include <Winbase.h>
int gettimeofday(struct timeval *tp, void *tzp)
{
	time_t clock;
	struct tm tm;
	SYSTEMTIME wtm;
	GetLocalTime(&wtm);
	tm.tm_year = wtm.wYear - 1900;
	tm.tm_mon = wtm.wMonth - 1;
	tm.tm_mday = wtm.wDay;
	tm.tm_hour = wtm.wHour;
	tm.tm_min = wtm.wMinute;
	tm.tm_sec = wtm.wSecond;
	tm.tm_isdst = -1;
	clock = mktime(&tm);
	tp->tv_sec = (long)clock;
	tp->tv_usec = wtm.wMilliseconds * 1000;
	return (0);
}
#endif

MyCLog::~MyCLog()
{
	close();
	if (m_szBuf != NULL)
	{
		delete[] m_szBuf;
		m_szBuf = NULL;
	}
}

MyCLog::MyCLog()
{
	m_file_level = log_close;
	m_print_level = log_close;
	m_bNewLine = true;				//默认自动换行, 不用在行末加\n
	m_bNewDaySwitch = true;			//默认自动每天切换日志文件

	m_log_line_pos = 0;
	m_log_max_line = MAX_LOG_LINE;
	m_log_name_index = 0;

	memset(m_filepath, 0, sizeof(m_filepath));
	memset(m_prefix, 0, sizeof(m_prefix));
	memset(m_logdir, 0, sizeof(m_logdir));

	time_t t = time(NULL);
	struct tm *_tm = localtime(&t);
	memcpy(&m_date, _tm, sizeof(m_date));

	if (m_log_fd) {
		fprintf(stderr, "fclose m_log_fd\n");
		fclose(m_log_fd);
	}
	m_log_fd = NULL;
	m_szBuf = NULL;
	m_nBufferSize = -1;	// 默认使用系统缓存
}

int MyCLog::setLogHeader(const char *name)
{
	// 日志的文件名产生规则：prefix_时间年月日_进程ID_日志计数.log
	int len = (int)strlen(name);
	if ( len >= sizeof(m_prefix) )
		return -1;
	if (len == 0)
		return -1;
	strcpy(m_prefix, name);
	m_log_name_index = 0;
	if (m_log_fd != NULL)
	{
		fflush(m_log_fd);
		fclose(m_log_fd);
		m_log_fd = NULL;
	}
	return 0;
}

int MyCLog::_canAccessDir(const char *dir)
{
	int len = (int)strlen(dir);

	if (len <= 0 || len >= PATH_MAX)
	{
		fprintf(stderr, "_canAccessDir failed to get lenth of dir %s\n", dir);
		return -1;
	}

#ifndef _WIN32
	DIR *pdir = NULL;
	if ((pdir = opendir(dir)) == NULL)
	{
		if (mkdir(dir, LOG_DIR_MODE) == -1)
		{
			fprintf(stderr, "setLogDir failed to make sub directory %s\n", dir);
			return -1;
		}
	}
	else
	{
		if (closedir(pdir) < 0)
		{
			fprintf(stderr, "Unable to close directory %s\n", dir);
		}
		pdir = NULL;
	}
#endif

	if (access(dir, W_OK) < 0)
	{
		fprintf(stderr, "can not access dir:%s\n", dir);
		return -1;
	}

	return 0;
}

int MyCLog::setLogDir(const char *dir)
{
	int nRet = _canAccessDir(dir);
	if (nRet < 0)	return nRet;

	strncpy(m_logdir, dir, sizeof(m_logdir));
	return 0;
}


/*
m_nBufferSize = -1或不设置: 默认使用系统
m_nBufferSize =	0: 使用系统默认
m_nBufferSize > 0: 使用缓存
*/
int MyCLog::setLogBufferSize(unsigned int size)
{
	//删除文件缓存前先flush，再close文件句柄
	close();

	if (m_szBuf != NULL)
		delete[] m_szBuf;

	m_nBufferSize = size;
	m_szBuf = NULL;
	if (m_nBufferSize > 0)
	{
		m_szBuf = new char[m_nBufferSize];
		if (m_szBuf == NULL)
		{
			fprintf(stderr, "new char error.reason:%d--%s:\n", errno, strerror(errno));
			return -1;
		}
		memset(m_szBuf, 0, m_nBufferSize);
	}
	return 0;
}

int MyCLog::_logOpen()
{
	close();

	snprintf(m_filepath, PATH_MAX, "%s/%s_%04d%02d%02d_%d_%d.log", m_logdir, m_prefix, m_date.tm_year+1900, m_date.tm_mon+1, m_date.tm_mday, getpid(), m_log_name_index);

	if (strlen(m_logdir) == 0) {
		fprintf(stderr, "len of m_logdir == 0. m_logdir:%s\n", m_logdir);
		return -1;
	}

	char tmp_path[PATH_MAX];
	snprintf(tmp_path, sizeof(tmp_path), "%s.tmp", m_filepath);

	m_log_fd = fopen(tmp_path, "wb");

	if (m_log_fd == NULL)
	{
		fprintf(stderr, "fopen error. file:%s, reason:%d--%s\n", tmp_path, errno, strerror(errno));
		return -1;
	}

	///设置文件缓存
	if (m_nBufferSize > 0)
	{
		if (setvbuf(m_log_fd, m_szBuf, _IOFBF, m_nBufferSize) < 0)
		{
			fprintf(stderr, "setvbuf error.size=%d, file:%s, reason:%d--%s\n", m_nBufferSize, tmp_path, errno, strerror(errno));
			return -1;
		}
	}
	else if (m_nBufferSize == 0)	// no buffer
	{
		if (setvbuf(m_log_fd, NULL, _IONBF, 0) < 0)
		{
			fprintf(stderr, "setvbuf error.size=%d, file:%s, reason:%d--%s\n", m_nBufferSize, tmp_path, errno, strerror(errno));
			return -1;
		}
	}

	m_log_name_index++;	// New Log文件名后缀 1, 2, 3...
	return 0;
}

int MyCLog::close()
{
	if (m_log_fd == NULL)
		return 0;

	char tmp_path[PATH_MAX] = { 0 };
	if (fflush(m_log_fd) < 0)
	{
		fprintf(stderr, "fflush error.reason:%d--%s\n", errno, strerror(errno));
	}
	fclose(m_log_fd);
	m_log_fd = NULL;
	snprintf(tmp_path, sizeof(tmp_path), "%s.tmp", m_filepath);
	if (rename(tmp_path, m_filepath) < 0)
	{
		fprintf(stderr, "rename error.tmp_path:tmp_path:%s, reason:%d--%s\n", tmp_path, errno, strerror(errno));
		return -1;
	}
	return 0;
}

int MyCLog::get_fileno()
{
	if( m_log_fd == NULL) return -1;
	else return fileno(m_log_fd);
}

int MyCLog::logWithoutFormat(int level, const char *msg) //写日志
{
	if (level > log_critical && level < log_trace)
		return 0;

	struct timeval now;
	gettimeofday(&now, 0);
	const time_t sec = now.tv_sec;
	struct tm * _tm = localtime(&sec);

	if (m_log_fd == NULL)
	{
		if (_logOpen() < 0)
			return -1;
	}
	else if (m_log_line_pos >= m_log_max_line)
	{
		if (_logOpen() < 0)
			return -1;
		m_log_line_pos = 0;
	}

	if (m_date.tm_mday != _tm->tm_mday || m_date.tm_mon != _tm->tm_mon || m_date.tm_year != _tm->tm_year)
	{
		// 日期改变，重新计数
		m_log_name_index = 0;
		memcpy(&m_date, _tm, sizeof(m_date));
		if (m_bNewDaySwitch)
		{
			if (_logOpen() < 0)
				return -1;
		}
	}

	if (m_bNewLine)
	{
		if (fprintf(m_log_fd, "%04d-%02d-%02d %02d:%02d:%02d.%06d [%s] %s\n", _tm->tm_year+1900, _tm->tm_mon+1, _tm->tm_mday, _tm->tm_hour, _tm->tm_min, _tm->tm_sec, now.tv_usec, LOG_LEVEL[level / 10], msg) <= 0)
		{
			close();
			fprintf(stderr, "I/O (fprintf) error! %d--%s\n", errno, strerror(errno));
			return -1;
		}
	}
	else
	{
		if (fprintf(m_log_fd, "%04d-%02d-%02d %02d:%02d:%02d.%06d [%s] %s", _tm->tm_year+1900, _tm->tm_mon+1, _tm->tm_mday, _tm->tm_hour, _tm->tm_min, _tm->tm_sec, now.tv_usec, LOG_LEVEL[level / 10], msg) <= 0)
		{
			close();
			fprintf(stderr, "I/O (fprintf) error! %d--%s\n", errno, strerror(errno));
			return -1;
		}
	}

	m_log_line_pos++;
	return 0;
}

int MyCLog::log(int level, const char *format, ...) //写日志
{
	if (level > log_critical && level < log_trace)
		return 0;

	struct timeval now;
	gettimeofday(&now, 0);
	const time_t sec = now.tv_sec;
	struct tm * _tm = localtime(&sec);

	if (m_log_fd == NULL)
	{
		if (_logOpen() < 0)
			return -1;
	}
	else if (m_log_line_pos >= m_log_max_line)
	{
		if (_logOpen() < 0)
			return -1;
		m_log_line_pos = 0;
	}

	if (m_date.tm_mday != _tm->tm_mday || m_date.tm_mon != _tm->tm_mon || m_date.tm_year != _tm->tm_year)
	{
		// 日期改变，重新计数
		m_log_name_index = 0;
		memcpy(&m_date, _tm, sizeof(m_date));
		if (m_bNewDaySwitch)
		{
			if (_logOpen() < 0)
				return -1;
		}
	}

	if (fprintf(m_log_fd, "%04d-%02d-%02d %02d:%02d:%02d.%06d [%s] ", _tm->tm_year+1900, _tm->tm_mon+1, _tm->tm_mday, _tm->tm_hour, _tm->tm_min, _tm->tm_sec, now.tv_usec, LOG_LEVEL[level / 10]) <= 0)
	{
		close();
		fprintf(stderr, "I/O (fprintf) error! %d--%s\n", errno, strerror(errno));
		return -1;
	}

	va_list argp;
	va_start(argp, format);
	vfprintf(m_log_fd, format, argp);
	va_end(argp);

	if (m_bNewLine)
		fprintf(m_log_fd, "\n");

	m_log_line_pos++;
	return 0;
}

int MyCLog::println(int level, const char *format, ...) //写终端
{
	if (level > log_critical && level < log_trace)
		return 0;

	struct timeval now;
	gettimeofday(&now, 0);

	const time_t sec = now.tv_sec;
	struct tm * _tm = localtime(&sec);

    //[D] 24d 23:44:21.719797
	if (fprintf(stdout, "%04d-%02d-%02d %02d:%02d:%02d.%06d [%s] ", _tm->tm_year+1900, _tm->tm_mon+1, _tm->tm_mday, _tm->tm_hour, _tm->tm_min, _tm->tm_sec, now.tv_usec, LOG_LEVEL[level / 10]) <= 0)
	{
		close();
		fprintf(stderr, "I/O (fprintf) error! %d--%s\n", errno, strerror(errno));
		return -1;
	}

	va_list argp;
	va_start(argp, format);
	vfprintf(stdout, format, argp);
	va_end(argp);

	if (m_bNewLine)
		fprintf(stdout, "\n");

	return 0;
}

int MyCLog::flush()
{
	if (m_log_fd != NULL)
		return fflush(m_log_fd);
	return -1;
}

inline int _get_level_by_string(const char* level)
{
	if (strcasecmp(level, "trace") == 0) {
		return log_trace;
	}
	else if (strcasecmp(level, "debug") == 0) {
		return log_debug;
	}
	else if (strcasecmp(level, "info") == 0) {
		return log_info;
	}
	else if (strcasecmp(level, "warn") == 0) {
		return log_warn;
	}
	else if (strcasecmp(level, "error") == 0) {
		return log_error;
	}
	else if (strcasecmp(level, "critical") == 0) {
		return log_critical;
	}
	else if (strcasecmp(level, "close") == 0) {
		return log_close;
	}
	else {
		return log_trace;
	}
}

int MyCLog::setLogLevel(const char* file_level, const char* term_level)
{
	m_file_level = _get_level_by_string(file_level);
	m_print_level = _get_level_by_string(term_level);
	printf("setLogLevel. file_level:%s (%d), term_level:%s (%d)\n", file_level, m_file_level, term_level, m_file_level);
	return 0;
}

int MyCLog::setLogMaxLine(unsigned int limit)
{
	m_log_max_line = limit;
	return 0;
}

/*------------------------------------------------------------------------------------------
			下面为测试例子:
-------------------------------------------------------------------------------------------*/
int main(int argc, char* argv[])
{
	int ret = -1;
	MyCLog clog;
	ret = clog.setLogHeader("test");
	if (ret < 0) {
		return -1;
	}
	ret = clog.setLogLevel("debug", "debug");
	if (ret < 0) {
		return -1;
	}

	ret = clog.setLogDir("E:\\cygwin64\\home\\zlx\\code\\mybase\\myclog\\Debug");
	if (ret < 0) {
		return -1;
	}

	ret = clog.setLogBufferSize(10240);
	if (ret < 0) {
		return -1;
	}

	ret = clog.setLogMaxLine(100000);
	if (ret < 0) {
		return -1;
	}

	int total = 0;
	int i = 1;
	while (1) {
		char *p = "adbfe";
		clog.log(log_debug, p);
		total += (int)strlen(p);
		if (total / 1000 == i) {
			i++;
			printf("sleep 5s\n");
			sleep(5000);
		}
	}
	return 0;
}
