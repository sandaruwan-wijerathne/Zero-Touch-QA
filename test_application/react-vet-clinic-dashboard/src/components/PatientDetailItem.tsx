// src/components/PatientDetailItem.tsx
import Typography from '@mui/material/Typography';

type PatientDetailItemProps = {
  label: string;
  data: string;
};

export default function PatientDetailItem({
  label,
  data,
}: PatientDetailItemProps) {
  return (
    <Typography variant='body1' gutterBottom>
      <strong>{label}: </strong>
      <span>{data}</span>
    </Typography>
  );
}
