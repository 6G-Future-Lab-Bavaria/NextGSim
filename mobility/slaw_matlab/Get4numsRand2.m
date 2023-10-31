function [numbers] = Get4numsRand2(tot, vars)

% =======================
gran = 0.01;
Error = 0.03;
Thresh = 30;
% =======================

numbers = [0 0 0 0];
ii=0;
if vars >= 4
	aa = ceil(rand*4);
	numbers(aa) = tot;
elseif vars <= 0
	numbers = floor(tot/4)*ones(1,4);
	for ia = 1:4
		if sum(numbers) == tot
			return;
		end
		numbers(ia) = numbers(ia) + 1;
	end
else

	%=== Flatter Method ===================
	for ia = 0:gran:1
		for ib = (1-ia)/3:gran:1-ia
			for ic=(1-ia-ib)/2:gran:1-ia-ib
				%======================================
				id=(1-ia-ib-ic);
				zz=[ia ib ic id];

				if abs(vars - var(zz/mean(zz),1)) < Error*vars
					ii=ii+1;
					yy(ii,1:4) = zz;
					if ii > Thresh
						break;
					end
				end
			end
			if ii > Thresh
				break;
			end
		end
		if ii > Thresh
			break;
		end
	end

end

% ================================
% Randomize Solution
% ================================
yylen = size(yy,1);
xx = yy(ceil(yylen*rand),1:4);

% ================================
% Randomize Probability Slot (xx)
% ================================
temp = rand(1,4);
[tmp ord] = sort(temp, 'descend');
xx = xx(ord);

% ==========================================
% Distribute Total spots in Prability Slots
% ==========================================
xcum = [xx(1) sum(xx(1:2)) sum(xx(1:3)) sum(xx)];
for iz=1:tot
	dice = rand;
	for iy = 1:4
		if dice <= xcum(iy)
			numbers(iy) = numbers(iy) + 1;
			break;
		end
	end
end
%var(xx/mean(xx)) % NV verification
return;
