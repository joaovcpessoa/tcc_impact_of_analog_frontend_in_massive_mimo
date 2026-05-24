function [y] = amplify_signal_twt(x, type, chi_A, kappa_A, chi_phi, kappa_phi)
    
    switch upper(type)
        case 'IDEAL'
            y = x;
        case 'TWT'
            g_A = (chi_A .* abs(x)) ./ (1 + kappa_A .* abs(x).^2);
            g_phi = (chi_phi .* abs(x).^2) ./ (1 + kappa_phi .* abs(x).^2);
            y = g_A .* exp(1i * (angle(x) + g_phi));
        otherwise
            error('Invalid amplifier type.');
    end
end