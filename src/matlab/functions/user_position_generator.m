function [x,y] = user_position_generator(n_coord,R)
    
    r = sqrt(3)/2*R;
    
    aux_cord = rand(n_coord,1);
    
    K_1 = sum(aux_cord < 1/3);
    K_2 = sum(aux_cord < 2/3 & aux_cord > 1/3);
    
    u = rand(n_coord,1);
    v = rand(n_coord,1);
    
    u_1 = u(1:K_1,1);
    v_1 = v(1:K_1,1);
    
    u_2 = u(K_1+1:K_1+K_2,1);
    v_2 = v(K_1+1:K_1+K_2,1);
    
    u_3 = u(K_1+K_2+1:n_coord,1);
    v_3 = v(K_1+K_2+1:n_coord,1);
    
    x_1 = -R/2*u_1 + R*v_1;
    y_1 = r*u_1;
    
    x_2 = -R/2*u_2 - R/2*v_2;
    y_2 = -r*u_2 + r*v_2;
    
    x_3 = R*u_3 - R/2*v_3;
    y_3 = -r*v_3;
    
    x = [x_1' x_2' x_3']';
    y = [y_1' y_2' y_3']';

end