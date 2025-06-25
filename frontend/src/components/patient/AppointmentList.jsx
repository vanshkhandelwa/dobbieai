import React from 'react';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Badge,
  Flex,
  Text,
  Skeleton,
  IconButton,
  useDisclosure,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay
} from '@chakra-ui/react';
import { RepeatIcon } from '@chakra-ui/icons';

const AppointmentList = ({ appointments, isLoading, onCancelAppointment, onRefresh }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [appointmentToCancel, setAppointmentToCancel] = React.useState(null);
  const cancelRef = React.useRef();

  const handleCancelClick = (appointment) => {
    setAppointmentToCancel(appointment);
    onOpen();
  };

  const confirmCancel = () => {
    if (appointmentToCancel) {
      onCancelAppointment(appointmentToCancel.id);
    }
    onClose();
  };

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  // Format time for display
  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Get badge color based on status
  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled':
        return 'blue';
      case 'completed':
        return 'green';
      case 'cancelled':
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={4}>
        <Text fontSize="xl">Upcoming Appointments</Text>
        <IconButton
          icon={<RepeatIcon />}
          aria-label="Refresh"
          size="sm"
          onClick={onRefresh}
          isLoading={isLoading}
        />
      </Flex>
      
      {isLoading ? (
        [...Array(3)].map((_, i) => (
          <Skeleton key={i} height="50px" mb={2} />
        ))
      ) : appointments.length > 0 ? (
        <Box overflowX="auto">
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Doctor</Th>
                <Th>Date</Th>
                <Th>Time</Th>
                <Th>Status</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {appointments.map((appointment) => (
                <Tr key={appointment.id}>
                  <Td>Dr. {appointment.doctor_name}</Td>
                  <Td>{formatDate(appointment.appointment_time)}</Td>
                  <Td>{formatTime(appointment.appointment_time)}</Td>
                  <Td>
                    <Badge colorScheme={getStatusColor(appointment.status)}>
                      {appointment.status}
                    </Badge>
                  </Td>
                  <Td>
                    {appointment.status === 'scheduled' && (
                      <Button
                        colorScheme="red"
                        size="sm"
                        onClick={() => handleCancelClick(appointment)}
                      >
                        Cancel
                      </Button>
                    )}
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      ) : (
        <Box p={4} textAlign="center" borderWidth="1px" borderRadius="md">
          <Text>No appointments found</Text>
        </Box>
      )}
      
      {/* Cancel Confirmation Dialog */}
      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Cancel Appointment
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure you want to cancel this appointment? This action cannot be undone.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                No, Keep It
              </Button>
              <Button colorScheme="red" onClick={confirmCancel} ml={3}>
                Yes, Cancel It
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  );
};

export default AppointmentList;