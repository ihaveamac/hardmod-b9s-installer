#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#ifdef WIN32
#include <fcntl.h>
#include <io.h>
#endif

uint8_t* fileRead(const char* path, size_t *size)
{
	uint8_t *buffer = NULL;
	FILE *f = fopen(path, "rb");
	if (!f) return NULL;

	fseek(f, 0, SEEK_END);
	size_t filesize = ftell(f);
	fseek(f, 0, SEEK_SET);

	buffer = (uint8_t*)malloc(filesize);
	if (!buffer) {*size = 0; return NULL;}

	fread(buffer, 1, filesize, f);
	fclose(f);

	*size = filesize;

	return buffer;
}

void fileWriteStdout(void *buffer, size_t buffer_size)
{
#ifdef WIN32
	int res = setmode(fileno(stdout), O_BINARY);
	if (res == -1)
	{
		fprintf(stderr, "Unable to re-open stdout in binary mode, skipping write\n");
		return;
	}
#endif
	fwrite(buffer, 1, buffer_size, stdout);
}

void fileWrite(const char* path, void* buffer, size_t buffer_size)
{
	if (!buffer) { return; }
	FILE *f = fopen(path, "wb");
	if (!f) return;

	fwrite(buffer, 1, buffer_size, f);
	fclose(f);
}

int main(int argc, char** argv)
{
	if(argc < 3)
	{
		printf("Usage: %s file1 file2 [outputfile]\n", argv[0]);
		return 0;
	}

	char* file1 = argv[1];
	size_t file1size = 0;
	char* file2 = argv[2];
	size_t file2size = 0;

	uint8_t* buffer1 = fileRead(file1, &file1size);
	uint8_t* buffer2 = fileRead(file2, &file2size);
	if (buffer1 && buffer2)
	{
		size_t counter = 0;
		while (counter < file1size)
		{
			buffer1[counter] ^= buffer2[counter];
			counter++;
		}

		if (argc == 4)
		{
			fileWrite(argv[3], buffer1, file1size);
		}
		else
		{
			fileWriteStdout(buffer1, file1size);
		}
	}

	free(buffer1);
	free(buffer2);

	return 0;
}
