function clist = crand(n, k)
% function clist = crand(n, k);
% choose k from n in a uniform manner

clist=[];

if k > n
    disp('... k should not be larger than n');
    return;
end

while 1
    isAlreadyIn=0;
    tmp=ceil(rand*n);
    for i=1:length(clist)
        if clist(i)==tmp
            isAlreadyIn=1;
            break;
        end
    end
    if isAlreadyIn==0
        clist=[clist tmp];
    end
    if length(clist)==k
        break;
    end
end			