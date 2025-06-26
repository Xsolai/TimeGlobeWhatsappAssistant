import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Chip,
  IconButton,
  Divider,
  Alert,
  LinearProgress,
  Tooltip
} from '@mui/material';
import {
  ExpandMore,
  Download,
  Description,
  Gavel,
  Business,
  Euro,
  Security,
  Info,
  CheckCircle,
  Print,
  PictureAsPdf
} from '@mui/icons-material';

interface ContractSection {
  id: string;
  title: string;
  icon: React.ReactNode;
  content: string | React.ReactNode;
  required?: boolean;
}

interface ContractViewerProps {
  contractType: 'main' | 'dataProcessing' | 'sepa';
  title: string;
  description: string;
  sections: ContractSection[];
  onScrollComplete?: () => void;
  showDownload?: boolean;
  onDownload?: () => void;
  isDownloading?: boolean;
}

const ContractViewer: React.FC<ContractViewerProps> = ({
  contractType,
  title,
  description,
  sections,
  onScrollComplete,
  showDownload = true,
  onDownload,
  isDownloading = false
}) => {
  const [expandedSections, setExpandedSections] = useState<string[]>([]);
  const [readSections, setReadSections] = useState<string[]>([]);
  const [scrollProgress, setScrollProgress] = useState(0);
  const contentRef = useRef<HTMLDivElement>(null);

  // Auto-expand first section
  useEffect(() => {
    if (sections.length > 0 && expandedSections.length === 0) {
      setExpandedSections([sections[0].id]);
    }
  }, [sections]);

  // Track scroll progress
  const handleScroll = () => {
    if (contentRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = contentRef.current;
      const progress = (scrollTop / (scrollHeight - clientHeight)) * 100;
      setScrollProgress(Math.min(progress, 100));
      
      if (progress >= 95 && onScrollComplete) {
        onScrollComplete();
      }
    }
  };

  const handleAccordionChange = (sectionId: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    if (isExpanded) {
      setExpandedSections([...expandedSections, sectionId]);
      setReadSections(prev => {
        const newSections = [...prev];
        if (!newSections.includes(sectionId)) {
          newSections.push(sectionId);
        }
        return newSections;
      });
    } else {
      setExpandedSections(expandedSections.filter(id => id !== sectionId));
    }
  };

  const expandAll = () => {
    setExpandedSections(sections.map(s => s.id));
    setReadSections(sections.map(s => s.id));
  };

  const collapseAll = () => {
    setExpandedSections([]);
  };

  const allSectionsRead = readSections.length === sections.length;

  const getContractIcon = () => {
    switch (contractType) {
      case 'main':
        return <Gavel sx={{ fontSize: 28 }} />;
      case 'dataProcessing':
        return <Security sx={{ fontSize: 28 }} />;
      case 'sepa':
        return <Euro sx={{ fontSize: 28 }} />;
      default:
        return <Description sx={{ fontSize: 28 }} />;
    }
  };

  return (
    <Paper
      elevation={0}
      sx={{
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 2,
        overflow: 'hidden',
        backgroundColor: '#fafafa'
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 3,
          backgroundColor: 'white',
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, flex: 1 }}>
                          <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2,
                  backgroundColor: 'rgba(0, 0, 0, 0.05)',
                  color: 'rgba(0, 0, 0, 0.87)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                {getContractIcon()}
              </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                {title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {description}
              </Typography>
            </Box>
          </Box>
          
          {showDownload && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Als PDF herunterladen">
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={isDownloading ? null : <PictureAsPdf />}
                  onClick={onDownload}
                  disabled={isDownloading}
                  sx={{
                    borderColor: 'primary.main',
                    color: 'primary.main',
                    '&:hover': {
                      backgroundColor: 'primary.light'
                    }
                  }}
                >
                  {isDownloading ? 'Wird generiert...' : 'PDF'}
                </Button>
              </Tooltip>
              <Tooltip title="Drucken">
                <IconButton size="small" onClick={() => window.print()}>
                  <Print />
                </IconButton>
              </Tooltip>
            </Box>
          )}
        </Box>

        {/* Progress and Actions */}
        <Box sx={{ mt: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="caption" color="text.secondary">
              {readSections.length} von {sections.length} Abschnitten gelesen
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button size="small" onClick={expandAll} sx={{ fontSize: '0.75rem' }}>
                Alle öffnen
              </Button>
              <Button size="small" onClick={collapseAll} sx={{ fontSize: '0.75rem' }}>
                Alle schließen
              </Button>
            </Box>
          </Box>
          <LinearProgress
            variant="determinate"
            value={(readSections.length / sections.length) * 100}
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: 'action.hover',
              '& .MuiLinearProgress-bar': {
                borderRadius: 3,
                backgroundColor: allSectionsRead ? 'success.main' : 'primary.main'
              }
            }}
          />
          {allSectionsRead && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
              <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
              <Typography variant="caption" color="success.main">
                Alle Abschnitte wurden gelesen
              </Typography>
            </Box>
          )}
        </Box>
      </Box>

      {/* Content */}
      <Box
        ref={contentRef}
        onScroll={handleScroll}
        sx={{
          maxHeight: '400px',
          overflowY: 'auto',
          backgroundColor: 'white',
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: 'action.hover',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: 'action.selected',
            borderRadius: '4px',
            '&:hover': {
              backgroundColor: 'action.disabled',
            }
          }
        }}
      >
        {sections.map((section, index) => (
          <Accordion
            key={section.id}
            expanded={expandedSections.includes(section.id)}
            onChange={handleAccordionChange(section.id)}
            elevation={0}
            sx={{
              '&:before': {
                display: 'none',
              },
              '&.Mui-expanded': {
                margin: 0,
              },
              borderBottom: index < sections.length - 1 ? '1px solid' : 'none',
              borderColor: 'divider'
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMore />}
              sx={{
                px: 3,
                '&.Mui-expanded': {
                  minHeight: 56,
                },
                '& .MuiAccordionSummary-content': {
                  my: 1.5,
                  alignItems: 'center',
                  gap: 2
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                <Box sx={{ color: 'rgba(0, 0, 0, 0.87)' }}>
                  {section.icon}
                </Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 500, flex: 1 }}>
                  {section.title}
                </Typography>

                {readSections.includes(section.id) && (
                  <CheckCircle sx={{ fontSize: 20, color: 'success.main' }} />
                )}
              </Box>
            </AccordionSummary>
            <AccordionDetails sx={{ px: 3, pb: 3 }}>
              <Box sx={{ pl: 5 }}>
                {typeof section.content === 'string' ? (
                  <Typography
                    variant="body2"
                    sx={{
                      color: 'text.secondary',
                      whiteSpace: 'pre-line',
                      lineHeight: 1.7
                    }}
                  >
                    {section.content}
                  </Typography>
                ) : (
                  section.content
                )}
              </Box>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>

      {/* Scroll Indicator */}
      {scrollProgress < 95 && (
        <Box
          sx={{
            position: 'sticky',
            bottom: 0,
            left: 0,
            right: 0,
            py: 1,
            px: 3,
            backgroundColor: 'rgba(0, 0, 0, 0.03)',
            borderTop: '1px solid',
            borderColor: 'rgba(0, 0, 0, 0.12)',
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}
        >
          <Info sx={{ fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="caption" color="text.secondary">
            Bitte scrollen Sie nach unten, um den gesamten Vertrag zu lesen
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default ContractViewer; 