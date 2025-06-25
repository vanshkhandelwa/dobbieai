import React, { useState } from 'react';
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
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Textarea
} from '@chakra-ui/react';
import { RepeatIcon, EditIcon } from '@chakra-ui/icons';
import { appointmentService } from '../../services/api';

const AppointmentList = ({ appointments, isLoading, onRefresh }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [diagnosis, setDiagnosis] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  const handleUpdateClick = (appointment) => {
    setSelectedAppointment(appointment);
    setDiagnosis(appointment.diagnosis || '');
    onOpen();
  };

  const handleUpdateAppointment = async () => {
    setIsUpdating(true);
    try {
      await appointmentService.updateAppointment(selectedAppointment.id, {
        status: 'completed',
        diagnosis
      });
      onRefresh();
      onClose();
    } catch (error) {
      console.error('Error updating appointment:', error);
    } finally {
      setIsUpdating(false);
    }
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
        <Text fontSize="xl">Appointments</Text>
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
                <Th>Patient</Th>
                <Th>Date</Th>
                <Th>Time</Th>
                <Th>Reason</Th>
                <Th>Status</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {appointments.map((appointment) => (
                <Tr key={appointment.id}>
                  <Td>{appointment.patient_name}</Td>
                  <Td>{formatDate(appointment.appointment_time)}</Td>
                  <Td>{formatTime(appointment.appointment_time)}</Td>
                  <Td>{appointment.reason || 'Not specified'}</Td>
                  <Td>
                    <Badge colorScheme={getStatusColor(appointment.status)}>
                      {appointment.status}
                    </Badge>
                  </Td>
                  <Td>
                    {appointment.status === 'scheduled' && (
                      <Button
                        leftIcon={<EditIcon />}
                        colorScheme="green"
                        size="sm"
                        onClick={() => handleUpdateClick(appointment)}
                      >
                        Complete
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
      
      {/* Update Appointment Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Complete Appointment</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {selectedAppointment && (
              <>
                <Text mb={4}>
                  Patient: <strong>{selectedAppointment.patient_name}</strong><br />
                  Date: <strong>{formatDate(selectedAppointment.appointment_time)}</strong><br />
                  Time: <strong>{formatTime(selectedAppointment.appointment_time)}</strong>
                </Text>
                
                {selectedAppointment.symptoms && (
                  <Box mb={4}>
                    <Text fontWeight="bold">Symptoms:</Text>
                    <Text>{selectedAppointment.symptoms}</Text>
                  </Box>
                )}
                
                <FormControl>
                  <FormLabel>Diagnosis & Notes</FormLabel>
                  <Textarea
                    value={diagnosis}
                    onChange={(e) => setDiagnosis(e.target.value)}
                    placeholder="Enter diagnosis and treatment notes"
                    rows={5}
                  />
                </FormControl>
              </>
            )}
          </ModalBody>

          <ModalFooter>
            <Button mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button
              colorScheme="green"
              isLoading={isUpdating}
              onClick={handleUpdateAppointment}
            >
              Complete Appointment
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default AppointmentList;