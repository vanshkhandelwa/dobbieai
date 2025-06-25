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
  FormErrorMessage,
  RadioGroup,
  Radio,
  Stack,
  Switch,
  FormHelperText,
  Select
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    role: 'patient',
    specialization: '',
    date_of_birth: '',
    medical_history: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();
  const toast = useToast();
  const { register } = useAuth();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user types
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleRoleChange = (value) => {
    setFormData(prev => ({ ...prev, role: value }));
  };

  const validate = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Invalid email address';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    if (!formData.full_name) {
      newErrors.full_name = 'Full name is required';
    }
    
    if (formData.role === 'doctor' && !formData.specialization) {
      newErrors.specialization = 'Specialization is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Prepare data for registration
      const userData = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name
      };
      
      if (formData.role === 'doctor') {
        userData.specialization = formData.specialization;
      } else {
        userData.date_of_birth = formData.date_of_birth || null;
        userData.medical_history = formData.medical_history || null;
      }
      
      // Register user
      await register(userData, formData.role === 'doctor');
      
      setIsLoading(false);
      
      toast({
        title: 'Registration successful',
        description: 'Please log in with your new account',
        status: 'success',
        duration: 3000,
        isClosable: true
      });
      
      navigate('/login');
      
    } catch (error) {
      setIsLoading(false);
      
      toast({
        title: 'Registration failed',
        description: error.response?.data?.detail || 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
      
      console.error('Registration error:', error);
    }
  };

  return (
    <Box 
      minH="100vh" 
      display="flex" 
      alignItems="center" 
      justifyContent="center"
      bg="gray.50"
      py={10}
    >
      <Box 
        p={8} 
        maxW="500px" 
        w="100%" 
        bg="white" 
        borderRadius="lg" 
        boxShadow="md"
      >
        <VStack spacing={6} as="form" onSubmit={handleSubmit}>
          <Heading textAlign="center">Create an Account</Heading>
          
          <RadioGroup onChange={handleRoleChange} value={formData.role}>
            <Stack direction="row">
              <Radio value="patient">Patient</Radio>
              <Radio value="doctor">Doctor</Radio>
            </Stack>
          </RadioGroup>
          
          <FormControl id="email" isRequired isInvalid={!!errors.email}>
            <FormLabel>Email</FormLabel>
            <Input 
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
            />
            <FormErrorMessage>{errors.email}</FormErrorMessage>
          </FormControl>
          
          <FormControl id="full_name" isRequired isInvalid={!!errors.full_name}>
            <FormLabel>Full Name</FormLabel>
            <Input 
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="Enter your full name"
            />
            <FormErrorMessage>{errors.full_name}</FormErrorMessage>
          </FormControl>
          
          <FormControl id="password" isRequired isInvalid={!!errors.password}>
            <FormLabel>Password</FormLabel>
            <InputGroup>
              <Input 
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleChange}
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
            <FormErrorMessage>{errors.password}</FormErrorMessage>
          </FormControl>
          
          <FormControl id="confirmPassword" isRequired isInvalid={!!errors.confirmPassword}>
            <FormLabel>Confirm Password</FormLabel>
            <Input 
              type={showPassword ? 'text' : 'password'}
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm your password"
            />
            <FormErrorMessage>{errors.confirmPassword}</FormErrorMessage>
          </FormControl>
          
          {formData.role === 'doctor' && (
            <FormControl id="specialization" isRequired isInvalid={!!errors.specialization}>
              <FormLabel>Specialization</FormLabel>
              <Select 
                name="specialization"
                value={formData.specialization}
                onChange={handleChange}
                placeholder="Select specialization"
              >
                <option value="General Physician">General Physician</option>
                <option value="Cardiologist">Cardiologist</option>
                <option value="Dermatologist">Dermatologist</option>
                <option value="Neurologist">Neurologist</option>
                <option value="Pediatrician">Pediatrician</option>
                <option value="Psychiatrist">Psychiatrist</option>
                <option value="Orthopedic">Orthopedic</option>
                <option value="Gynecologist">Gynecologist</option>
                <option value="Ophthalmologist">Ophthalmologist</option>
                <option value="ENT Specialist">ENT Specialist</option>
              </Select>
              <FormErrorMessage>{errors.specialization}</FormErrorMessage>
            </FormControl>
          )}
          
          {formData.role === 'patient' && (
            <>
              <FormControl id="date_of_birth">
                <FormLabel>Date of Birth</FormLabel>
                <Input 
                  type="date"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                />
              </FormControl>
              
              <FormControl id="medical_history">
                <FormLabel>Medical History (Optional)</FormLabel>
                <Input 
                  name="medical_history"
                  value={formData.medical_history}
                  onChange={handleChange}
                  placeholder="Any relevant medical history"
                />
                <FormHelperText>
                  This will help doctors better understand your health background
                </FormHelperText>
              </FormControl>
            </>
          )}
          
          <Button 
            type="submit" 
            colorScheme="blue" 
            width="100%" 
            isLoading={isLoading}
          >
            Create Account
          </Button>
          
          <Text textAlign="center">
            Already have an account?{' '}
            <Link as={RouterLink} to="/login" color="blue.500">
              Sign In
            </Link>
          </Text>
        </VStack>
      </Box>
    </Box>
  );
};

export default Register;