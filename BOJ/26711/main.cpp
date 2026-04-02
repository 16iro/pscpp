#include <bits/stdc++.h>
using namespace std;

int ctoi(char c) {
    return c - '0';
}
char itoc(int i) {
    return i + '0';
}

void solve() {
    string a, b;
    string result = "";
    cin >> a >> b;

    int a_i = a.length() - 1;
    int b_i = b.length() - 1;
    int adder = 0;
    while (a_i >= 0 || b_i >= 0) {
        int a_digit = a_i < 0 ? 0 : ctoi(a[a_i]);
        int b_digit = b_i < 0 ? 0 : ctoi(b[b_i]);
        int num = a_digit + b_digit + adder;
        adder = num / 10;
        result = itoc(num % 10) + result;
        a_i--;
        b_i--;
    }
    cout << result;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    solve();

    return 0;
}
