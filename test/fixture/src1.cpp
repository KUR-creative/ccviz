#include <iostream>
#include <vector>
#include <fstream>

using namespace std;

void draw_line(char **fo, int dimension){

    for(int i=0;i<dimension;++i){
        for(int j=0;j<dimension;++j){
            cout<<fo[i][j]<<" ";
        }
        cout<<endl;
    }
}
void input_data(vector<int> &v, vector<int> &h, vector<int> &dp, vector<int> &dm, int &dimension) {
    ifstream in("ct.inp");

    if (in.is_open()) {
        in >> dimension;
        for(int i=0;i<2;++i){
            for(int j=0;j<dimension; ++j){
                int temp;
                in >> temp;
                if(i == 0)
                    v.push_back(temp);
                else
                    h.push_back(temp);  
            }
        }

        for(int i=0;i<2;++i){
            for(int j=0;(j<dimension*2 -1); ++j){
                int temp;
                in >> temp;
                if(i == 0)
                    dm.push_back(temp);
                else
                    dp.push_back(temp); 
            }
        }
    }
    else {
        cout << "can't find file" << endl;
    }
    in.close();
}
void next_x_y(int &x, int &y, int dimension){
    if(y==dimension-1){
        x++;
        y=0;
    }
    else
        y++;
    
}
bool check_is_correct(char** fo, int dimension, vector<int> &dp, vector<int> &dm, vector<int> &v, vector<int> &h){
    
    vector<int> temp_dp;
    vector<int> temp_dm;
    vector<int> temp_v;
    vector<int> temp_h;
    
    for(int i=0;i<dp.size();++i){
        if(i<dimension){
            int num_B=0;
            for(int m=0,n=i;n>=0;m++,n--){
                if(fo[m][n]=='B') num_B++;
            }
            temp_dp.push_back(num_B);
        }
        else{
            int num_B=0;
            for(int m=i-dimension+1,n=dimension-1;m<dimension;m++,n--){
                if(fo[m][n]=='B') num_B++;
            }
            temp_dp.push_back(num_B);
        }  
    }
    
    for(int i=0;i<dm.size();++i){
        if(i<dimension){
            int num_B=0;
            for(int m=0,n=dimension-i-1;n<dimension;++n,++m){
                if(fo[m][n] =='B') num_B++; 
            }
            temp_dm.push_back(num_B);
        }
        else{
            int num_B=0;
            for(int m=i-dimension+1,n=0;m<dimension;++m,++n){
                if(fo[m][n] =='B') num_B++;
            }
            temp_dm.push_back(num_B);
        }   
    }

    for(int i=0;i<v.size();++i){
        int num_B=0;
        for(int j=0;j<dimension;++j){
            if(fo[j][i]=='B') num_B++;
        }
        temp_v.push_back(num_B);
    }

    for(int i=0;i<h.size();++i){
        int num_B=0;
        for(int j=0;j<dimension;++j){
            if(fo[i][j]=='B') num_B++;
        }
        temp_h.push_back(num_B); 
    }

    int i;
    for(i=0;i<dp.size() && dp[i]==temp_dp[i];++i);     
        if(i<dp.size())return false;
    for(i=0;i<dm.size() && dm[i]==temp_dm[i];++i);
        if(i<dm.size())return false;
    for(i=0;i<h.size() && h[i]==temp_h[i];++i);
        if(i<h.size())return false;     
    for(i=0;i<v.size() && v[i]==temp_v[i];++i);
        if(i<v.size())return false;

    return true;
}
void init_object(char** fo, int dimension, vector<int> &dp, vector<int> &dm, vector<int> &v, vector<int> &h){
    if(dp.front()==1) fo[0][0]='B';
    else fo[0][0]='-';
    if(dp.back()==1) fo[dimension-1][dimension-1]='B';
    else fo[dimension-1][dimension-1]='-';
    if(dm.front()==1) fo[0][dimension-1]='B';
    else fo[0][dimension-1]='-';
    if(dm.back()==1) fo[dimension-1][0] ='B';
    else fo[dimension-1][0]='-';

    
    int p = 0;
    int q = 0;
    
    for(int i=0;i<dp.size();++i){
        
        if(i<dimension){
            if(dp[i]==0){
                for(int m=0,n=i;n>=0;m++,n--) {
                    fo[m][n] = '-';
                }
                
            }
            else if(dp[i]==i+1){
                for(int m=0,n=i;n>=0;m++,n--){
                    fo[m][n] = 'B';
                }
                
            }
        }

        else{
            if(dp[i]==0){
                for(int m=i-dimension+1,n=dimension-1;m<dimension;m++,n--){
                    fo[m][n] = '-';
                }
                
            }
            else if(dp[i]==i-(2*p+1)){
                for(int m=i-dimension+1,n=dimension-1;m<dimension;m++,n--){
                    fo[m][n] = 'B'; 
                }
            }
            p++;
        } 
    }
    
    for(int i=0;i<dm.size();++i){
        if(i<dimension){
            if(dm[i]==0){
                for(int m=0,n=dimension-i-1;n<dimension;++n,++m){
                    fo[m][n]='-';   
                }
            }

            else if(dm[i]==i+1){
                for(int m=0,n=dimension-i-1;n<dimension;++n,++m){
                    fo[m][n]='B';    
                }
            }
        }

        else{
             if(dm[i]==0){
                 for(int m=i-dimension+1,n=0;m<dimension;++m,++n){
                     fo[m][n]='-';  
                 }
            }
            
            else if(dm[i]==i-(2*q+1)){
                for(int m=i-dimension+1,n=0;m<dimension;++m,++n){
                     fo[m][n]='B';
                }
            }
            q++;

        }
        
    }
    
    for(int i=0;i<v.size();++i){
        if(v[i]==0){
            for(int j=0;j<dimension;++j){
                fo[j][i] = '-';
            }
        }
        else if(v[i]==dimension){
            for(int j=0;j<dimension;++j){
                fo[j][i] = 'B';
            }
        }
    }
    
    for(int i=0;i<h.size();++i){
        if(h[i]==0){
            for(int j=0;j<dimension;++j){
                fo[i][j] = '-';
            }
        }
        else if(h[i]==dimension){
            for(int j=0;j<dimension;++j){
                fo[i][j] = 'B';
            }
        }
    }    
}
bool check_allLine(char** fo, int dimension){
    int i;
    int j;
   
    for(i=0;i<dimension;++i){
        for(j=0;j<dimension;++j){
            if(fo[i][j] == 'Y') break;
        }
        if(fo[i][j] == 'Y') break;
    }
    if(i<dimension || j<dimension)
        return false;
   return true;  
}
bool check_hole(char **temp,int dimension,int x, int y){
    if(temp[x][y]=='-') temp[x][y] = 'H';

    if(x-1>=0 && y>=0 && temp[x-1][y]=='-')check_hole(temp,dimension,x-1,y);
    if(x>=0 && y-1>=0 && temp[x][y-1]=='-')check_hole(temp,dimension,x,y-1);
    if(x>=0 && y+1<dimension && temp[x][y+1]=='-')check_hole(temp,dimension,x,y+1);
    if(x+1<dimension && y>=0 && temp[x+1][y]=='-')check_hole(temp,dimension,x+1,y);
    
}
bool check_oneCell(char **temp, int dimension,int x, int y){
    if(temp[x][y]=='B') temp[x][y] = 'C';

    if(x-1>=0 && y-1>=0 && temp[x-1][y-1]=='B') check_oneCell(temp,dimension,x-1,y-1);
    if(x-1>=0 && y>=0 && temp[x-1][y]=='B')check_oneCell(temp,dimension,x-1,y);
    if(x-1>=0 && y+1<dimension && temp[x-1][y+1]=='B')check_oneCell(temp,dimension,x-1,y+1);
    if(x>=0 && y-1>=0 && temp[x][y-1]=='B')check_oneCell(temp,dimension,x,y-1);
    if(x>=0 && y+1<dimension && temp[x][y+1]=='B')check_oneCell(temp,dimension,x,y+1);
    if(x+1<dimension && y-1>=0 && temp[x+1][y-1]=='B')check_oneCell(temp,dimension,x+1,y-1);
    if(x+1<dimension && y>=0 && temp[x+1][y]=='B')check_oneCell(temp,dimension,x+1,y);
    if(x+1<dimension && y+1<dimension && temp[x+1][y+1]=='B')check_oneCell(temp,dimension,x+1,y+1);

}
bool check_verticalLine(char** fo, vector<int> &v, int dimension, int y, int &c_x, int &c_y){
    int num_B=0;
    int num_Y=0;
    int num_minus=0;

    for(int i=0;i<dimension;++i){
        if(fo[i][y]=='B')
            num_B++;
        else if(fo[i][y]=='Y')
            num_Y++;
        else
            num_minus++;
        
        
    }

    if(num_B > v[y]||num_minus > dimension - v[y]){
        return false;
    } 
    if(num_Y==0)return true;
    
    if(num_B == v[y]){
        for(int i=0;i<dimension;++i){
            if(fo[i][y]=='Y'){
                fo[i][y] = '-';
                num_minus++;
            }
        }
        if(num_B > v[y]||num_minus > dimension - v[y])return false;
        return true;
    }
    else{
        if(num_Y == v[y]-num_B){
            for(int i=0;i<dimension;++i){
                if(fo[i][y]=='Y'){
                    fo[i][y] = 'B';
                    num_B++;
                }
            }
            if(num_B > v[y]||num_minus > dimension - v[y])return false;
            return true;
        }
        else{
            int i;
            for(i=0;i<dimension;++i){
                if(fo[i][y]=='Y'){
                    break;
                }
            }
            c_x = i;
            c_y = y;
            return true;
        }
    }
}
bool check_horizontalLine(char** fo, vector<int> &h, int dimension, int x, int &c_x, int &c_y){
    int num_B=0;
    int num_Y=0;
    int num_minus = 0;

    for(int i=0;i<dimension;++i){
        if(fo[x][i]=='B')
            num_B++;
        else if(fo[x][i]=='Y')
            num_Y++;
        else
            num_minus++;   
    }

    if(num_B > h[x] || num_minus > dimension - h[x]){
        return false;
    }
    if(num_Y==0) {  
        return true;
    }

    if(num_B == h[x]){
        for(int i=0;i<dimension;++i){
            if(fo[x][i]=='Y'){
                fo[x][i] = '-';
                num_minus++;
            } 
        }
        if(num_B > h[x] || num_minus > dimension - h[x]){
                return false;
            }
        return true;
    }

    else{
        if(num_Y == h[x]-num_B){
            for(int i=0;i<dimension;++i){
                if(fo[x][i]=='Y'){
                    fo[x][i] = 'B';
                    num_B++;
                }
            }
            if(num_B > h[x] || num_minus > dimension - h[x]){
                return false;
            }
            return true;
        }
        else{
            int i;
            for(i=0;i<dimension;++i){
                if(fo[x][i]=='Y'){
                    break;
                }
            }          
            c_x = x;
            c_y = i;

            return true;
        }

    }
}
bool check_diagonalPlusLine(char** fo, vector<int> &dp, int dimension, int x, int y,int &c_x, int &c_y){
    int num_B=0;
    int num_Y=0;
    int num_minus = 0;
    int length=0;

    if(x+y<dimension){
        for(int i=0,j=x+y;j>=0;--j,++i){
            if(fo[i][j] =='B') num_B++;
            else if(fo[i][j] == 'Y') num_Y++;
            else num_minus++;
            length++;
        }
    }
    else{
        for(int i=x+y-dimension+1,j=dimension-1;i<dimension;++i,--j){
            if(fo[i][j] =='B') num_B++;
            else if(fo[i][j] == 'Y') num_Y++;
            else num_minus++;
            length++;
        }
    }
    if(num_B > dp[x+y] || num_minus > length - dp[x+y]){
        return false;
    }
    if(num_Y == 0)return true;

    if(num_B == dp[x+y]){
        if(x+y<dimension){
            int i,j;
            for(i=0,j=x+y;j>=0;--j,++i){
                if(fo[i][j]=='Y'){
                    fo[i][j] = '-';
                    num_minus++;
                }
            }
            if(num_B > dp[x+y] || num_minus > length - dp[x+y]) return false;     
            return true;         
        }
        else{
            int i,j;
            for(i=x+y-dimension+1,j=dimension-1;i<dimension;++i,--j){
                if(fo[i][j]=='Y'){
                    fo[i][j] = '-';
                    num_minus++;
                }
            }
            if(num_B > dp[x+y] || num_minus > length - dp[x+y]){
                return false;
            }
            return true;      
        }
    }
    else{
        if(num_Y == dp[x+y]-num_B){
            if(x+y<dimension){
                int i,j;
                for(i=0,j=x+y;j>=0;--j,++i){
                    if(fo[i][j]=='Y'){
                        fo[i][j] = 'B';
                        num_B++;
                    }
                }
                if(num_B > dp[x+y] || num_minus > length - dp[x+y]){
                    return false;
                }
                return true;        
            }
            else{
                int i,j;
                for(i=x+y-dimension+1,j=dimension-1;i<dimension;++i,--j){
                    if(fo[i][j]=='Y'){
                        fo[i][j] = 'B';
                        num_B++;
                    }
                }
                    if(num_B > dp[x+y] || num_minus > length - dp[x+y]){
                    return false;
                }
                return true;
            }  
        }
        else{
            if(x+y<dimension){
                int i,j;
                for(i=0,j=x+y;j>=0&&fo[i][j]!='Y';--j,++i);
                c_x = i;
                c_y = j;
                return true;        
            }
            else{
                int i,j;
                for(i=x+y-dimension+1,j=dimension-1;i<dimension&&fo[i][j]!='Y';++i,--j);
                c_x = i;
                c_y = j;
                return true;
            }      
        }
    }
}
bool check_diagonalMinusLine(char** fo, vector<int> &dm, int dimension, int x, int y,int &c_x, int &c_y){
    int num_B=0;
    int num_Y=0;
    int num_minus = 0;
    int length=0;
    int match_point;

    if(x==y)
        match_point = dimension-1;
    else if(x<y)
        match_point = dimension - (y-x) - 1;
    else
        match_point = dimension + (x-y) - 1; 
    if(x<=y){
        for(int i=0,j=y-x;j<dimension;++j,++i){
            if(fo[i][j] =='B') num_B++;
            else if(fo[i][j] == 'Y') num_Y++;
            else num_minus++;
            length++;
        }
    }
    else{
        for(int i=x-y,j=0;i<dimension;++i,++j){
            if(fo[i][j] =='B') num_B++;
            else if(fo[i][j] == 'Y') num_Y++;
            else num_minus++;
            length++;
        }
    }

    if(num_B > dm[match_point] || num_minus > length - dm[match_point]){
        return false;
    }

    if(num_Y==0)return true;

    if(num_B == dm[match_point]){
        if(x<=y){
            int i,j;
            for(i=0,j=y-x;j<dimension;++j,++i){
                if(fo[i][j]=='Y'){
                    fo[i][j] = '-';
                    num_minus++;
                }
            } 
            if(num_B > dm[match_point] || num_minus > length - dm[match_point]) return false;
            return true;        
        }
        else{
            int i,j;
            for(i=x-y,j=0;i<dimension;++i,++j){
                if(fo[i][j]=='Y'){
                    fo[i][j] = '-';
                    num_minus++;
                }
            }
            if(num_B > dm[match_point] || num_minus > length - dm[match_point]) return false;
            return true; 
        }
    }
    else{
        if(num_Y == dm[match_point]-num_B){
            if(x<=y){
                int i,j;
                for(i=0,j=y-x;j<dimension;++j,++i){
                    if(fo[i][j]=='Y'){
                        fo[i][j] = 'B';
                        num_B++;
                    }
                }
                if(num_B > dm[match_point] || num_minus > length - dm[match_point]) return false;
                return true;        
            }
            else{
                int i,j;
                for(i=x-y,j=0;i<dimension;++i,++j){
                    if(fo[i][j]=='Y'){
                        fo[i][j] = 'B';
                        num_B++;
                    }
                }
                if(num_B > dm[match_point] || num_minus > length - dm[match_point]) return false;
                return true;
            }   
        }
        else{
            if(x<=y){
                int i,j;
                for(i=0,j=y-x;j<dimension && fo[i][j] != 'Y';++j,++i);
                c_x = i;
                c_y = j;
                return true;  
                      
            }
            else{
                int i,j;
                for(i=x-y,j=0;i<dimension&& fo[i][j] != 'Y';++i,++j);
                c_x = i;
                c_y = j;
                return true;
            }  
        }
    }
}
bool find_object(char** fo, vector<int> &v, vector<int> &h, vector<int> &dp, vector<int> &dm, int dimension,int x, int y){
    int change_x = -1;   
    int change_y = -1;

    char **temp_fo = new char*[dimension];
    int temp_x;
    int temp_y;
    for(int i = 0; i < dimension; ++i)
        temp_fo[i] = new char[dimension];
    
   
    if(check_verticalLine(fo, v, dimension, y, change_x, change_y) == false) return false;   
    if(check_horizontalLine(fo, h, dimension, x, change_x, change_y)==false) return false; 
    if(check_diagonalPlusLine(fo, dp,dimension, x, y,change_x,change_y)==false) return false;  
    if(check_diagonalMinusLine(fo, dm,dimension, x, y,change_x,change_y)==false) return false;

    for(int i=0;i<dimension; ++i){
        for(int j=0; j<dimension; ++j){
            temp_fo[i][j] = fo[i][j];
        }
    }

    if(change_x != -1 && change_y != -1){
        fo[change_x][change_y] = 'B';
        temp_x = x;
        temp_y = y;
        next_x_y(x,y,dimension);
        bool check = find_object(fo,v,h,dp,dm,dimension,x,y);
        if(check==false){
            for(int i=0;i<dimension; ++i){
                for(int j=0; j<dimension; ++j){
                    fo[i][j] = temp_fo[i][j];
                }
            }
            x=temp_x;
            y=temp_y;
            fo[change_x][change_y] = '-';
            next_x_y(x,y,dimension);
            bool check = find_object(fo,v,h,dp,dm,dimension,x,y);
            if(check==false) return false;
            else {
                return true;
            }
            
        }
        else {
            return true;
        }
       
    }
    else{
        if(check_allLine(fo,dimension)==true) {
            int i,j;
            for(i=0;i<dimension;++i){
                for(j=0;j<dimension;++j){
                    if(fo[i][j]=='B')break;
                }
                if(fo[i][j]=='B')break;
            }          
            if(i<dimension || j<dimension) check_oneCell(temp_fo,dimension,i,j);
            for(i=0;i<dimension;++i){
                for(j=0;j<dimension;++j){
                    if(temp_fo[i][j]=='B')break;
                }
                if(temp_fo[i][j]=='B')break;
            }
            if(i<dimension || j<dimension) return false;

            for(int i=0;i<dimension;++i){
                if(temp_fo[0][i]=='-') check_hole(temp_fo,dimension,0,i);
            }
            for(int i=0;i<dimension;++i){
                if(temp_fo[i][dimension-1]=='-')check_hole(temp_fo,dimension,i,dimension-1);
            }
            for(int i=0;i<dimension;++i){
                if(temp_fo[dimension-1][i]=='-')check_hole(temp_fo,dimension,dimension-1,i);
            }
            for(int i=0;i<dimension;++i){
                if(temp_fo[i][0]=='-')check_hole(temp_fo,dimension,i,0);
            }

            for(i=0;i<dimension;++i){
                for(j=0;j<dimension;++j){
                    if(temp_fo[i][j]=='-')break;
                }
                if(temp_fo[i][j]=='-')break;
            }
            if(i<dimension || j<dimension) {
                return false;
            }
            bool check = check_is_correct(fo,dimension,dp,dm,v,h);
            if(check==false)return false;
            return true;
        }
        next_x_y(x,y,dimension);
        if(find_object(fo,v,h,dp,dm,dimension,x,y)==false)
            return false;
        else
        {
            return true;
        }        
    }
    return true;
}
void out_data(char **fo, int dimension){
    ofstream out("ct.out");
    for(int i=0;i<dimension;++i){
        for(int j=0;j<dimension;++j){
            out<<fo[i][j]<<" ";
        }
        out<<endl;
    }
    out.close();
}
int main(void){
    int dimension;
    char **object;
    vector<int> vertical_line;
    vector<int> horizontal_line;
    vector<int> diagonalPlus_line;
    vector<int> diagonalMinus_line;

    input_data(vertical_line, horizontal_line, diagonalPlus_line, diagonalMinus_line, dimension); // work well!!
    object = new char*[dimension];
        for(int i = 0; i < dimension; ++i)
            object[i] = new char[dimension];
        
        for(int i=0;i<dimension; ++i){
            for(int j=0; j<dimension; ++j){
                object[i][j] = 'Y';
         }
    }
    init_object(object,dimension,diagonalPlus_line,diagonalMinus_line,vertical_line,horizontal_line);//초기화
    find_object(object, vertical_line, horizontal_line, diagonalPlus_line, diagonalMinus_line, dimension, 0 ,0);
    out_data(object,dimension);
    for(int i = 0; i < dimension; ++i){ 
        delete [] object[i];
    } delete [] object;
}
