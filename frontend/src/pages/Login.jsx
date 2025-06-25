import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  Text,
  Link,
  useToast,
  InputGroup,
  InputRightElement,
  IconButton,
  FormErrorMessage
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const navigate = useNavigate();
  const toast = useToast();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    
    try {
      const userData = await login(email, password);
      
      setIsLoading(false);
      
      toast({
        title: 'Login successful',
        description: `Welcome back, ${userData.full_name}`,
        status: 'success',
        duration: 3000,
        isClosable: true
      });
      
      // Redirect based on user role
      if (userData.role === 'doctor') {
        navigate('/doctor-dashboard');
      } else {
        navigate('/patient-dashboard');
      }
      
    } catch (error) {
      setIsLoading(false);
      setError('Invalid email or password');
      console.error('Login error:', error);
    }
  };

  return (
    <Box 
      minH="100vh" 
      display="flex" 
      alignItems="center" 
      justifyContent="center"
      bg="gray.50"
    >
      <Box 
        p={8} 
        maxW="400px" 
        w="100%" 
        bg="white" 
        borderRadius="lg" 
        boxShadow="md"
      >
        <VStack spacing={6} as="form" onSubmit={handleSubmit}>
          <Heading textAlign="center">Doctor Appointment Assistant</Heading>
          <Text textAlign="center" color="gray.600">
            Sign in to your account
          </Text>
          
          {error && (
            <Text color="red.500" textAlign="center">
              {error}
            </Text>
          )}
          
          <FormControl id="email" isRequired isInvalid={error}>
            <FormLabel>Email</FormLabel>
            <Input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
            />
          </FormControl>
          
          <FormControl id="password" isRequired isInvalid={error}>
            <FormLabel>Password</FormLabel>
            <InputGroup>
              <Input 
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
              />
              <InputRightElement>
                <IconButton
                  icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                />
              </InputRightElement>
            </InputGroup>
          </FormControl>
          
          <Button 
            type="submit" 
            colorScheme="blue" 
            width="100%" 
            isLoading={isLoading}
          >
            Sign In
          </Button>
          
          <Text textAlign="center">
            Don't have an account?{' '}
            <Link as={RouterLink} to="/register" color="blue.500">
              Register here
            </Link>
          </Text>
        </VStack>
      </Box>
    </Box>
  );
};

export default Login;