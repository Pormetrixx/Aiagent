<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Cold Calling Agent - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
        }
        .login-container { 
            background: white; 
            padding: 3rem; 
            border-radius: 12px; 
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); 
            width: 100%; 
            max-width: 420px; 
            backdrop-filter: blur(10px);
        }
        .login-header { 
            text-align: center; 
            margin-bottom: 2rem; 
        }
        .login-header h1 { 
            color: #2c3e50; 
            margin-bottom: 0.5rem; 
            font-size: 1.8rem;
        }
        .login-header p {
            color: #7f8c8d;
            font-size: 1rem;
        }
        .form-group { 
            margin-bottom: 1.5rem; 
        }
        .form-group label { 
            display: block; 
            margin-bottom: 0.5rem; 
            font-weight: 600; 
            color: #2c3e50; 
        }
        .form-group input { 
            width: 100%; 
            padding: 0.9rem; 
            border: 2px solid #e1e8ed; 
            border-radius: 8px; 
            font-size: 1rem; 
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }
        .btn { 
            width: 100%; 
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white; 
            padding: 0.9rem; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 1rem; 
            font-weight: 600;
            margin-top: 1rem; 
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
        }
        .error { 
            color: #e74c3c; 
            text-align: center; 
            margin-bottom: 1rem; 
            padding: 0.75rem;
            background: #fdf2f2;
            border: 1px solid #fecaca;
            border-radius: 6px;
        }
        .info { 
            color: #7f8c8d; 
            text-align: center; 
            margin-top: 1.5rem; 
            font-size: 0.9rem; 
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 6px;
        }
        .features {
            margin-top: 1.5rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 6px;
            font-size: 0.85rem;
            color: #5a6c7d;
        }
        .features h4 {
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        .features ul {
            list-style: none;
            padding: 0;
        }
        .features li {
            padding: 0.2rem 0;
        }
        .features li::before {
            content: "✓ ";
            color: #27ae60;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>🤖 AI Agent Dashboard</h1>
            <p>Cold Calling Management System</p>
        </div>
        
        <?php if (isset($login_error)): ?>
            <div class="error"><?php echo htmlspecialchars($login_error); ?></div>
        <?php endif; ?>
        
        <form method="post">
            <input type="hidden" name="action" value="login">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autocomplete="username">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autocomplete="current-password">
            </div>
            <button type="submit" class="btn">🔑 Login to Dashboard</button>
        </form>
        
        <div class="info">
            <strong>Default credentials:</strong><br>
            Username: <code>admin</code><br>
            Password: <code>admin123</code>
        </div>
        
        <div class="features">
            <h4>Dashboard Features:</h4>
            <ul>
                <li>Real-time system monitoring</li>
                <li>Conversation script management</li>
                <li>FAQ database editing</li>
                <li>Customer relationship management</li>
                <li>Call history and analytics</li>
                <li>Asterisk PBX integration</li>
                <li>System configuration</li>
            </ul>
        </div>
    </div>
</body>
</html>