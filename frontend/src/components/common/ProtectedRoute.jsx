import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Box, Center, Spinner, Text } from '@chakra-ui/react';

const ProtectedRoute = ({ children, role }) => {
  const { user, isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <Center h="100vh">
        <Box textAlign="center">
          <Spinner size="xl" mb={4} />
          <Text>Loading...</Text>
        </Box>
      </Center>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  // Check role if specified
  if (role && user?.role !== role) {
    return <Navigate to={user?.role === 'doctor' ? '/doctor-dashboard' : '/patient-dashboard'} />;
  }

  return children;
};

export default ProtectedRoute;