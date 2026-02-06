// src/components/PatientDetails.tsx
import { useState } from 'react';
import { toast } from 'react-toastify';
import { Patient } from '../types';
import PatientDetailItem from './PatientDetailItem';
import { usePatientStore } from '../store';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Grow from '@mui/material/Grow';
import ConfirmDialog from './ConfirmDialog';

type PatientDetailsProps = {
  patient: Patient;
};

export default function PatientDetails({ patient }: PatientDetailsProps) {
  const deletePatient = usePatientStore(state => state.deletePatient);
  const getPatientById = usePatientStore(state => state.getPatientById);

  const [openConfirm, setOpenConfirm] = useState(false);

  const handleDelete = () => {
    setOpenConfirm(true);
  };

  const handleConfirmDelete = () => {
    deletePatient(patient.id);
    toast('Patient deleted', { type: 'error' });
    setOpenConfirm(false);
  };

  const handleCloseConfirm = () => {
    setOpenConfirm(false);
  };

  return (
    <>
      <Grow in={true} timeout={500}>
        <Paper elevation={3} sx={{ m: 2, p: 2 }}>
          <PatientDetailItem label='ID' data={patient.id} />
          <PatientDetailItem label='Name' data={patient.name} />
          <PatientDetailItem label='Owner' data={patient.caretaker} />
          <PatientDetailItem label='Email' data={patient.email} />
          <PatientDetailItem
            label='Admission Date'
            data={patient.date.toString()}
          />
          <PatientDetailItem label='Symptoms' data={patient.symptoms} />

          <Stack
            direction={{ xs: 'column', lg: 'row' }}
            spacing={2}
            justifyContent='space-between'
            sx={{ mt: 2 }}
          >
            <Button
              variant='contained'
              color='primary'
              onClick={() => getPatientById(patient.id)}
            >
              Edit
            </Button>
            <Button variant='contained' color='error' onClick={handleDelete}>
              Delete
            </Button>
          </Stack>
        </Paper>
      </Grow>
      <ConfirmDialog
        open={openConfirm}
        title='Confirm Deletion'
        content='Are you sure you want to delete this patient?'
        onConfirm={handleConfirmDelete}
        onClose={handleCloseConfirm}
      />
    </>
  );
}
