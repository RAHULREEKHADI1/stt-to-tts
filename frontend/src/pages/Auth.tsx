import React, { useState } from "react";
import Login from "../components/Login";
import Signup from "../components/Signup";

interface Props {
  onLogin: () => void;
}

const Auth: React.FC<Props> = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <>
      {isLogin ? (
        <Login 
          onLogin={onLogin} 
          onSwitch={() => setIsLogin(false)} 
        />
      ) : (
        <Signup 
          onSignupSuccess={() => setIsLogin(true)} 
        />
      )}
    </>
  );
};

export default Auth;