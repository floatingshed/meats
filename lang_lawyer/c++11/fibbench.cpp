#include <iostream>
#include <sstream>
#include <chrono>
#include <iomanip>
#include <locale>
#include <cmath>

// -std=c++11

#ifdef CNT
int g_calls;
#endif

int fib(int n)
{
#ifdef CNT
	++g_calls;
#endif
	if (n < 2)
	{
		return n;
	}
	return fib(n-1) + fib(n-2);
}

struct Numpunct: public std::numpunct<char>
{
protected:
	virtual char do_thousands_sep() const { return ','; }
	virtual std::string do_grouping() const { return "\003"; }
};
	
int main(int argc, char **argv)
{
	using namespace std::chrono;
	int n = 38;
	if (argc > 1)
	{
		std::istringstream(argv[1]) >> n;
	}
	high_resolution_clock::time_point start = high_resolution_clock::now();
	int fib_n = fib(n);
	// we need fib(n+1)
	int calls = fib_n * (1 + std::sqrt(5)) - 0.5;
	high_resolution_clock::time_point end = high_resolution_clock::now();
	duration<double> elapsed = duration_cast<duration<double>>(end - start);
	double secs = elapsed.count();
	std::cout << "fib(" << n << ") = " << fib_n << "; "
		<< std::setprecision(3) << secs << " s elapsed. ";
	std::cout.imbue({ std::locale(), new Numpunct() });
	std::cout << calls << " calls, "
#ifdef CNT
		<< g_calls << " (counted), "
#endif
		<< std::setprecision(0) << std::fixed << calls/secs << " c/s." 
		<<  std::endl;
	return 0;
}
