import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a response interceptor for handling token expiration
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // If we get an unauthorized response, clear the user session
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API services
const appointmentService = {
  getAppointments: (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value);
      }
    });
    
    return api.get(`/appointments?${params.toString()}`);
  },
  
  getAppointment: (id) => api.get(`/appointments/${id}`),
  
  createAppointment: (appointmentData) => api.post('/appointments', appointmentData),
  
  updateAppointment: (id, appointmentData) => api.put(`/appointments/${id}`, appointmentData),
  
  cancelAppointment: (id) => api.delete(`/appointments/${id}`),
  
  checkDoctorAvailability: (doctorName, date, timeOfDay) => {
    const params = new URLSearchParams();
    if (date) params.append('date', date);
    if (timeOfDay) params.append('time_of_day', timeOfDay);
    
    return api.get(`/appointments/availability/${encodeURIComponent(doctorName)}?${params.toString()}`);
  }
};

const doctorService = {
  getDoctors: () => api.get('/doctors'),
  
  getDoctor: (id) => api.get(`/doctors/${id}`),
  
  createDoctor: (doctorData) => api.post('/doctors', doctorData),
  
  updateDoctor: (id, doctorData) => api.put(`/doctors/${id}`, doctorData)
};

const patientService = {
  getPatients: () => api.get('/patients'),
  
  getPatient: (id) => api.get(`/patients/${id}`),
  
  createPatient: (patientData) => api.post('/patients', patientData),
  
  updatePatient: (id, patientData) => api.put(`/patients/${id}`, patientData)
};

const reportService = {
  generateDoctorReport: (reportRequest) => api.post('/reports/doctor-report', reportRequest),
  
  getDoctorStats: (doctorId, fromDate, toDate) => {
    const params = new URLSearchParams();
    if (fromDate) params.append('from_date', fromDate);
    if (toDate) params.append('to_date', toDate);
    
    return api.get(`/reports/stats/doctor/${doctorId}?${params.toString()}`);
  }
};

const chatService = {
  sendMessage: (prompt, conversationHistory = [], userId = null, role = null) => {
    return api.post('/chat', {
      prompt,
      conversation_history: conversationHistory,
      user_id: userId,
      role
    });
  }
};

export { api as default, appointmentService, doctorService, patientService, reportService, chatService };